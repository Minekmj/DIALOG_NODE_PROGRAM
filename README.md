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
pip install requirements.txt
```

그 다음

파일 경로에서

```bash
python3 run.py
```

입력 & 실행

## 스크린 샷

- 기본 노드

- 함수 노드

- 시작 노드

- 종료 노드

- 풀 세팅

- 시작 - 종료

- 시작 - 종료 (함수 라인)

- 대사 편집

- 내장 시뮬 이미지

## 한마디

- 버그 많음 (아마)
- 심심해서 만든 것
- 활용 마음데로
- 주석 제대로 있지 않음
