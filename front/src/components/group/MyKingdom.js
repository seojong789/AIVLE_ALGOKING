import React, { useState } from 'react'
import { Input } from 'antd'
import GroupCreateModal from './GroupCreateModal';
import GroupList from './GroupList'
import axios from 'axios';

export default function Group() {
  const [createGroupModalOn, setCreateGroupModalOn] = useState(false);
  const [name, setName] = useState("");
  const [nameError, setNameError] = useState("");


  const onChangeName = (event) => {
    setName(event.target.value);
    if (event.target.value !== "") {
      setNameError("")
    }
  };

  const requestClick = () => {
    const token = localStorage.getItem("access")
    const headers = { 'Authorization' : `Bearer ${token}` }

    axios.post(`http://localhost:8000/api/team/req/`,{"name":name}, { headers: headers })
        .then(response => {
            console.log(response)
        })
        .catch(error => {
            console.log(error);
        });
  }

  return (
    <>
        <GroupCreateModal show={createGroupModalOn} onHide={setCreateGroupModalOn} />
      
        {/* main content */}
        <h3 className="my_kingdom_header">🐊 나의 킹덤</h3>

        <div className='group_controller'>
            <div className='create_kingdom'>
                <button onClick={() => setCreateGroupModalOn(true)}><span>킹덤 건설하기</span></button>
            </div>

            <div className='group_search'>
                <span>킹덤 검색</span>
                <div className='search_member_input' onChange={onChangeName} >
                    <Input placeholder="가입할 킹덤명을 입력해 주세요." />
                </div>
                <button onClick={requestClick}>요청 보내기</button>
            </div>
        </div>
        <GroupList />
    </>
  );
}