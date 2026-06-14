# Dialog_Node_Program

DearPyGui를 사용한 대화 노드 프로그램

## .json 출력

```json
{
  "Functions": [
    "함수 1",
    "함수 2"
  ],
  "Dialogues": [
    {
      "DialogueIndex": 1,
      "DialogueType": 0, 
      "DialogueText": "대화 내용이 들어갑니다.",
      "HasResponse": true,
      "SpecialCode": "",
      "Position": [100.0, 100.0],
      "Responses": [
        {
          "ResponseText": "선택지 대답 1",
          "ResponseType": 0,
          "ResponseCode": "",
          "NextDialogueIndex": 2
        }
      ]
    }
  ]
}      
```

- DialogueType: 0 (Base), 1 (Function), 2 (Start), 3 (End)

- HasResponse: 응답(선택지) 보유 여부 (true / false)

- SpecialCode: DialogueType이 1이면 일반 텍스트, 2이면 숫자형 텍스트, 나머지는 ""

- Position: 에디터 내 노드 좌표 (무시 가능)

- ResponseType: 0 (Base), 1 (Function)

- ResponseCode: ResponseType이 0이면 "", 1이면 텍스트

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

![](image/%EA%B8%B0%EB%B3%B8%20%EC%9D%B4%EB%AF%B8%EC%A7%80.png)

- 기본 노드

![](image/%EA%B8%B0%EB%B3%B8%20%EB%85%B8%EB%93%9C.png)

- 함수 노드

![](image/%ED%95%A8%EC%88%98%20%EB%85%B8%EB%93%9C.png)

- 시작 노드

![](image/%EC%8B%9C%EC%9E%91%20%EB%85%B8%EB%93%9C.png)

- 종료 노드

![](image/%EC%A2%85%EB%A3%8C%20%EB%85%B8%EB%93%9C.png)

- 풀 세팅

![](image/%ED%92%80.png)

- 시작 - 종료

![](image/%EC%8B%9C%EC%9E%91-%EC%A2%85%EB%A3%8C.png)

- 시작 - 종료 (함수 라인)

![](image/%EC%8B%9C%EC%9E%91-%EC%A2%85%EB%A3%8C(%ED%95%A8%EC%88%98%20%EB%9D%BC%EC%9D%B8).png)

- 대사 편집

![](image/%EB%8C%80%EC%82%AC%20%ED%8E%B8%EC%A7%91.png)

- 내장 시뮬 이미지

![](image/%EC%8B%9C%EB%AE%AC.png)

## 한마디

- 활용 마음데로
- 주석 제대로 있지 않음
