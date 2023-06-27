import '../../scss/group.scss'
import 'bootstrap/dist/css/bootstrap.min.css';

import { React, useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";

const apiUrl = "http://localhost:8000/api/team/myteam/"

export default function GroupList() {
    const [groupList, setGroupList] = useState([]);
    const navigate = useNavigate();
    useEffect(() => {
        const token = localStorage.getItem("access")
            const headers = {
                'Authorization' : `Bearer ${token}`
            }
        axios.get(apiUrl, { headers: headers })
            .then(response => {
                const { data } = response
                setGroupList(data)
                console.log(data)
            })
            .catch(error => {
                console.log(error);
            });
    }, []);

    return (
        <>
            {groupList.length !== 0 ? (
                <div className="my_kingdom_list">
                    {groupList.map((group,idx) => {
                        const { team } = group;
                        const { id,name, num_members, description, leader,image } = team

                        const isOdd = idx%2===1 ? '' : 'kbBg'
                        
                        return (
                            <div className={`kingdomBox ${isOdd}`}>
                                <div className='kbTop'>
                                    <span>팀명 {name}</span>
                                    <button onClick={()=>navigate('/group/'+id)}>입장하기</button>
                                </div>
                                <div className='kbBottom'>
                                    <div className='kbMark'>
                                        <img src= {`http://localhost:8000${image}/`} className='' />
                                    </div>
                                    <div className='kbInfo'>
                                        <p>각오 {description}</p>
                                        <ul>
                                            <li><span className='info'>리더</span>{leader.username}</li>
                                            <li><span className='info'>푼 문제 수</span></li>
                                            <li><span className='info'>레이팅</span></li>
                                            <li><span className='info'>인원</span>{num_members}/{num_members}</li>
                                            <li><span className='info'>문제집 수</span></li>
                                        </ul>
                                    </div>
                                </div>
                            </div>
                        )
                    })}
                </div>
            ) : (
                <div className='nothingKingdom'>
                    <img src='/img/nothing_kingdom.png'/>
                    <span>현재 가입한 킹덤이 없습니다.</span>
                </div>
            )}
        </>
    );
}