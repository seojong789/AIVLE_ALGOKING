import numpy as np
import torch
from torch import optim
import random
from utils import *
from model import MultiDAE, loss_function_dae
from config import *
import json
import datetime
import time
import wandb

seed = args.seed
random.seed(seed)
np.random.seed(seed)
torch.manual_seed(seed)

wandb.init(project="Algoking", config={"model": "Multi-DAE",
                                       "batch_size": args.batch_size,
                                       "lr"        : args.lr,
                                       "epochs"    : args.n_epochs})
wandb.run.name = "MultiDAE"

device = torch.device("cuda:0")
n_items = load_n_items(args.dataset)
data = get_data(args.dataset)
train_data, valid_in_data, valid_out_data, test_in_data, test_out_data = data
N = train_data.shape[0] 
idxlist = list(range(N))

def train(model, criterion, optimizer, is_VAE=False):
        # Turn on training mode
        model.train()
        train_loss = 0.0
        global update_count

        np.random.shuffle(idxlist)

        for batch_idx, start_idx in enumerate(range(0, N, args.batch_size)):
            end_idx = min(start_idx + args.batch_size, N)

            data = train_data[idxlist[start_idx:end_idx]]
            data = naive_sparse2tensor(data).to(device)

            optimizer.zero_grad()

            if is_VAE:
                if args.total_anneal_steps > 0:
                    anneal = min(args.anneal_cap,
                                1. * update_count / args.total_anneal_steps)
                else:
                    anneal = args.anneal_cap

                optimizer.zero_grad()
                recon_batch, mu, logvar = model(data)
                loss = criterion(recon_batch, data, mu, logvar, anneal)
            else:
                recon_batch = model(data)
                loss = criterion(recon_batch, data)

            loss.backward()
            train_loss += loss.item()
            optimizer.step()

            update_count += 1

def evaluate(model, criterion, data_tr, data_te, is_VAE=False):
        # Turn on evaluation mode
        model.eval()
        total_loss = 0.0
        global update_count
        e_idxlist = list(range(data_tr.shape[0]))
        e_N = data_tr.shape[0]
        n100_list = []
        r10_list = []
        r20_list = []

        with torch.no_grad():
            for start_idx in range(0, e_N, args.batch_size):
                end_idx = min(start_idx + args.batch_size, N)
                data = data_tr[e_idxlist[start_idx:end_idx]]
                heldout_data = data_te[e_idxlist[start_idx:end_idx]]

                data_tensor = naive_sparse2tensor(data).to(device)
                if is_VAE:

                    if args.total_anneal_steps > 0:
                        anneal = min(args.anneal_cap,
                                    1. * update_count / args.total_anneal_steps)
                    else:
                        anneal = args.anneal_cap

                    recon_batch, mu, logvar = model(data_tensor)

                    loss = criterion(recon_batch, data_tensor, mu, logvar, anneal)

                else:
                    recon_batch = model(data_tensor)
                    loss = criterion(recon_batch, data_tensor)

                total_loss += loss.item()

                # Exclude examples from training set
                recon_batch = recon_batch.cpu().numpy()
                recon_batch[data.nonzero()] = -np.inf

                n100 = ndcg(recon_batch, heldout_data, 100)
                r10 = recall(recon_batch, heldout_data, 10)
                r20 = recall(recon_batch, heldout_data, 20)

                n100_list.append(n100)
                r10_list.append(r10)
                r20_list.append(r20)

        total_loss /= len(range(0, e_N, args.batch_size))
        n100_list = np.concatenate(n100_list)
        r10_list = np.concatenate(r10_list)
        r20_list = np.concatenate(r20_list)

        return total_loss, np.mean(n100_list), np.mean(r10_list), np.mean(r20_list)


p_dims = [200, 3000, n_items] 
item_tag_emb = pd.read_csv(args.dataset + '/item_tag_emb.csv')
model = MultiDAE(p_dims, tag_emb=item_tag_emb).to(device)

optimizer = optim.Adam(model.parameters(), lr=args.lr, weight_decay=args.wd)
criterion = loss_function_dae

# best_n100 = -np.inf
best_r20 = -np.inf
update_count = 0
early_stopping = args.early_stopping
stopping_cnt = 0

log_dir_name = str(datetime.datetime.now())[0:10] + '_dae'
log_dir = os.path.join(args.log_dir, log_dir_name)


if not os.path.exists(log_dir):
    os.makedirs(log_dir)

if not os.path.exists(args.save_dir):
    os.makedirs(args.save_dir)

for epoch in range(1, args.n_epochs + 1):
    epoch_start_time = time.time()
    train(model, criterion, optimizer, is_VAE=False)

    val_loss, n100, r10, r20 = evaluate(model, criterion, valid_in_data, valid_out_data, is_VAE=False)
    print('-' * 89)
    print('| end of epoch {:3d}/{:3d} | time: {:4.2f}s | valid loss {:4.4f} | '
        'n100 {:5.4f} | r10 {:5.4f} | r20 {:5.4f}'.format(
        epoch, args.n_epochs, time.time() - epoch_start_time, val_loss,
        n100, r10, r20))
    print('-' * 89)

    wandb.log({"multidae_r20": r20})

    if r20 > best_r20:
        with open(os.path.join(log_dir, 'best_multidae_' + args.save), 'wb') as f:
            torch.save(model.state_dict(), f)
            print(f"Best model saved! r@20 : {r20:.4f}")
        best_r20 = r20
        stopping_cnt = 0
    else:
        print(f'Stopping Count : {stopping_cnt} / {early_stopping}')
        stopping_cnt += 1

    if stopping_cnt > early_stopping:
        print('*****Early Stopping*****')
        break

# Load the best saved model.
with open(os.path.join(log_dir, 'best_multidae_' + args.save), 'rb') as f:
    model.load_state_dict(torch.load(f))

torch.save(model.state_dict(), args.save_dir + '/multidae.pth')

# Run on test data.
test_loss, n100, r10, r20 = evaluate(model, criterion, valid_in_data, valid_out_data, is_VAE=False)
print('=' * 89)
print('| End of training | test loss {:4.4f} | n100 {:4.4f} | r10 {:4.4f} | '
    'r20 {:4.4f}'.format(test_loss, n100, r10, r20))
print('=' * 89)

with open(os.path.join(log_dir, "update_count_dae.txt"), "w", encoding='utf-8') as f:
    f.write(str(update_count))


with open(args.dataset + '/model_score.json', 'r', encoding="utf-8") as f:
    model_score = json.load(f)

model_score['multidae'] = r20
with open(args.dataset + '/model_score.json', 'w', encoding="utf-8") as f:
    json.dump(model_score, f, ensure_ascii=False, indent="\t")