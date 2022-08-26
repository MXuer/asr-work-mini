# asr-work-mini
For my son, do asr and nlu annotation works.

## 添加波形显示功能

1. 自动播放
2. 循环播放
3. 显示波形







- [安装`pyaudio`](https://i.stack.imgur.com/Xn0bm.png)

  ```shell
  brew install portaudio
  python -m pip install --global-option='build_ext' --global-option='-I/opt/homebrew/Cellar/portaudio/19.7.0/include' --global-option='-L/opt/homebrew/Cellar/portaudio/19.7.0/lib' pyaudio
  ```

  

- [ ] 界面调整；

- [ ] 上一首下一首；
- [ ] 选定某一个语音；
- [ ] 波形播放进度；
- [x] 播放与暂停；
- [ ] 循环播放；
- [x] 波形背景图虚化；
