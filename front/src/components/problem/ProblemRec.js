import React, { useEffect, useState } from 'react';
import { Swiper, SwiperSlide } from 'swiper/react';
import { Navigation } from 'swiper';
import Tooltip from '@mui/material/Tooltip';
import Typography from '@mui/material/Typography';
import { Modal, Button, Table } from 'antd';
import { ThreeCircles } from  'react-loader-spinner'
import { HiOutlineArrowNarrowRight, HiStar, HiOutlineInformationCircle, HiOutlineHashtag } from "react-icons/hi";

import 'swiper/css';
import 'swiper/css/navigation';
import 'swiper/css/pagination';
import 'swiper/css/scrollbar';

import axios from 'axios';

export default function ProblemRec() {
  const [loading, setLoading] = useState(true)
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [username, setUsername] = useState('');
  const [problemList, setProblemList] = useState([]);
  const [moreProblemList, setMoreProblemList] = useState([]);

  const handleMoreButtonClick = () => {
    setIsModalOpen(true);
  };
  const handleModalCancel = () => {
    setIsModalOpen(false);
  };

  useEffect(() => {
    const token = localStorage.getItem('access');
    const headers = { 'Authorization': `Bearer ${token}` }

    axios
      .get('http://localhost:8000/api/problems/rec/', { headers: headers })
      .then((response) => {
        const { data } = response;
        setUsername(data.user);
        setProblemList(data.rec);
        setLoading(false)
      })
      .catch((error) => {
        console.log(error);
      });

    axios.get('http://localhost:8000/api/problems/rec/more/', { headers: headers })
      .then((response) => {
        const {data} = response

        let temp = []
        data.rec.map(item => {
          const { number, title, tier } = item.problem
          let tmp = { "number": number, "title": title, "tier": tier }
          temp.push(tmp)
        })
        setMoreProblemList(temp)
        console.log(temp)
      })
      .catch((error) => {
        console.log(error);
      })
  }, []);


  const columns = [
    {
      title: '문제 번호',
      dataIndex: 'number',
      key: 'number',
      align: "center",
      width: "135px",
    },
    {
      title: '문제 이름',
      dataIndex: 'title',
      key: 'title',
      align: "center",
    },
    {
      title: '티어',
      dataIndex: 'tier',
      key: 'tier',
      align: "center",
      width: "175px",
    },
    {
      title: '유형',
      dataIndex: 'type',
      key: 'type',
      align: "center",
      width: "210px",
    },
  ];
  
  const handleRowClick = (row) => {
    window.open(`https://www.acmicpc.net/problem/${row.number}`, '_blank')
  }

  return (
    <div className="problem-layout-01">
      <div className="problem-rec-layout">
        <div className="problem-rec-left">
          <h3>추천 문제</h3>
          <br />
          <span>{username} 님의</span>
          <br />
          <span>풀이 이력을 바탕으로</span>
          <br />
          <span>AI가 추천하는 문제에</span>
          <br />
          <span>도전해 보세요!</span>
          <br />
          <button className="rec-more-btn" onClick={handleMoreButtonClick}>
            추천 문제 더 보기 +
          </button>
        </div>

          {
            loading ?
            (
              <div className='loading'>
                <ThreeCircles
                  height="100"
                  width="100"
                  color="#75D779"
                  visible={true}
                  ariaLabel="three-circles-rotating"
                />
                <span>Generated by AI..</span>
              </div>
            ) : 
            (
              <>
            <div className='problem-rec-right'>
              <div className='prInfo'>
                <div className='info-icon'>
                  <HiOutlineInformationCircle size={21}/>
                </div>
                <span>추천 문제는 00시에 갱신됩니다.</span>
              </div>
              <Swiper
                className='problem-rec-swiper'
                modules={[Navigation]}
                slidesPerView={3}
                spaceBetween={0}
                navigation
              >
                {
                  problemList && problemList.map(pr => {

                    const { problem } = pr;
                    return (
                      <SwiperSlide className='problem-rec-swiperslide'>
                        <div className='problem-item' onClick={() => window.open(`https://www.acmicpc.net/problem/${problem.number}`, '_blank')}>
                          <div className='card-top'>
                            <div className='problem-item-icons'>
                              <div className='problem-item-star'><HiStar /></div>
                              <Tooltip title={
                                <Typography sx={{ color: 'white' }}>
                                  <span># 자료구조</span><br />
                                  <span># BFS</span><br />
                                </Typography>
                              }
                                arrow
                                placement='top-end'
                              >
                                <div className='problem-item-tag'
                                  id='problem-tag'
                                ><HiOutlineHashtag /></div>
                              </Tooltip>
                            </div>
                            <div className='problem-item-title'>{problem.title}</div>
                            <div className='problem-item-num font-PreR'>{problem.number}</div>
                          </div>

                          <div className='card-bottom font-PreR'>
                            <div className='problem-item-tier'>
                              <img src={`https://static.solved.ac/tier_small/${problem.level}.svg`} alt="bronze5"></img>
                              <span>{problem.tier}</span>
                            </div>
                            <div>
                              <div className='problem-item-info'>
                                <div>
                                  <span>제출자 수 :</span>
                                  <span>푼 사람 :</span>
                                  <span>평균 시도 :</span>
                                  <span>정답률 :</span>
                                </div>
                                <div>
                                  <span>999</span>
                                  <span>{problem.userCount}</span>
                                  <span>{problem.avgTreis}</span>
                                  <span>33.3%</span>
                                </div>
                              </div>
                            </div>
                          </div>
                        </div>
                      </SwiperSlide>
                    );
                  })

                }
                <SwiperSlide className='swiperslide-btn'>
                  <div className='gomore'>
                    <span><HiOutlineArrowNarrowRight size={30} fontWeight={100} /></span>
                    <span style={{ marginTop: '10px' }}>전체 보기</span>
                  </div>
                </SwiperSlide>
              </Swiper>
            </div>
              </>
            )
          }
      </div>

      <Modal 
        className='prModal'
        title={<span className='prmTitle'>추천 문제</span>}
        visible={isModalOpen}
        centered={true}
        onCancel={handleModalCancel}
        width={1050}
        footer={[
          <Button key="back" onClick={handleModalCancel}>
            닫기
          </Button>
        ]}
      >
        <Table 
          dataSource={moreProblemList}
          columns={columns}
          rowClassName={()=>'prItemRow'}
          onRow={(row, idx)=>({
            onClick: ()=> handleRowClick(row)
          })}
        />
      </Modal>
    </div>
  );
}
