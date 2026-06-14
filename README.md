# Dialog_Node_Program

## .json 출력

```json
{
    "Functions": [
        "함수 1", //string
        "함수 2",
          ...
    ],
    "Dialogues": [
        {
            "DialogueIndex": 1, //int
            "DialogueType": (int), //(0 : base, 1 : function, 2 : start, 3 : end)
            "DialogueText": "대화", //string 대화
            "HasResponse": (bool), //응답을 가지는지 (true -> 가진다, false -> 가지지 않는다)
            "SpecialCode": (string), //TYPE이 1이면 글, 2이면 숫자 글, 나머지 ""
            "Position": [ //무시. 에디터 용
                100.0,
                100.0
            ],
            "Responses": [ //대답 리스트
                {
                    "ResponseText": "대답 1", //string
                    "ResponseType": (int), //(0 : base, 1 : function)
                    "ResponseCode": (string), //TYPE이 0이면 "", TYPE이 1이면 글
                    "NextDialogueIndex": (int) //다음 연결 노드 -> DialogueIndex
                },
                           ...
            ]
        },
        ...
    ]
}
        
```

## 실행 방법

일단 라이브러리 설치

파일 경로에서

```bash
pip install -r requirements.txt
```

그 다음

파일 경로에서

```bash
python3 run.py
```

입력 & 실행

## 스크린 샷

![](https://github.com/Minekmj/DIALOG_NODE_PROGRAM/blob/main/image/%EA%B8%B0%EB%B3%B8%20%EC%9D%B4%EB%AF%B8%EC%A7%80.png)

- 기본 노드

![](https://github.com/Minekmj/DIALOG_NODE_PROGRAM/blob/main/image/%EA%B8%B0%EB%B3%B8%20%EB%85%B8%EB%93%9C.png)

- 함수 노드

![](https://github.com/Minekmj/DIALOG_NODE_PROGRAM/blob/main/image/%ED%95%A8%EC%88%98%20%EB%85%B8%EB%93%9C.png)

- 시작 노드

![](https://github.com/Minekmj/DIALOG_NODE_PROGRAM/blob/main/image/%EC%8B%9C%EC%9E%91%20%EB%85%B8%EB%93%9C.png)

- 종료 노드

![](https://github.com/Minekmj/DIALOG_NODE_PROGRAM/blob/main/image/%EC%A2%85%EB%A3%8C%20%EB%85%B8%EB%93%9C.png)

- 풀 세팅

![](https://github.com/Minekmj/DIALOG_NODE_PROGRAM/blob/main/image/%ED%92%80.png)

- 시작 - 종료

![](https://github.com/Minekmj/DIALOG_NODE_PROGRAM/blob/main/image/%EC%8B%9C%EC%9E%91-%EC%A2%85%EB%A3%8C.png)

- 시작 - 종료 (함수 라인)

![](https://github.com/Minekmj/DIALOG_NODE_PROGRAM/blob/main/image/%EC%8B%9C%EC%9E%91-%EC%A2%85%EB%A3%8C(%ED%95%A8%EC%88%98%20%EB%9D%BC%EC%9D%B8).png)

- 대사 편집

![](https://github.com/Minekmj/DIALOG_NODE_PROGRAM/blob/main/image/%EB%8C%80%EC%82%AC%20%ED%8E%B8%EC%A7%91.png)

- 내장 시뮬 이미지

![](https://github.com/Minekmj/DIALOG_NODE_PROGRAM/blob/main/image/%EC%8B%9C%EB%AE%AC.png)

## 한마디

- 버그 많음 (아마)
- 심심해서 만든 것
- 활용 마음데로
- 주석 제대로 있지 않음
