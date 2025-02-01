## DiscordChatBot

대화형 인공지능 디스코드 봇 프로젝트입니다.

OpenAI의 GPT-3.5-Turbo 모델을 활용중입니다.

TTS는 MeloTTS를 사용중

## Prerequisites
- A Windows system.
- Python == 3.9
- Anaconda installed.
- PyTorch installed.
- CUDA 11.x installed.

Pytorch install command:
```sh
pip install torch==1.13.1+cu117 torchaudio --extra-index-url https://download.pytorch.org/whl/cu117
```

CUDA 11.7 install:
`https://developer.nvidia.com/cuda-11-7-0-download-archive`

---

## Installation
1. **Create an Anaconda environment:**

```sh
conda create -n emremrchatbot python=3.9
```

2. **Activate the environment:**

```sh
conda activate emremrchatbot
```

3. **Clone this repository to your local machine:**

```sh
git clone https://github.com/emremrdl/emremrChatBot.git
```

4. **Navigate to the cloned directory:**

```sh
cd emremrChatBot
```

5. **Install the necessary dependencies:**

```sh
pip install -r requirements.txt
```

6. **Install FFmpeg:**

```sh
conda install ffmpeg
```

---

## Todo
- [x] 디스코드 봇 생성
- [x] LLM(Large-Language-Model) 탑재
- [x] TTS(Text-To-Speech) 모델 학습 및 탑재
- [ ] 여러 LLM 모델 선택기능
- [ ] 디스코드 음성 녹음
- [ ] Speech Recognition로 녹음된 음성 텍스트로 변환

---

## 참고자료
- [디스코드 봇 개발 일지 2023-02-17 - OpenAI / ChatGPT / GPT-3 로 챗봇 만들기](https://syerco0.com/33)
- [MeloTTS](https://github.com/myshell-ai/MeloTTS)
