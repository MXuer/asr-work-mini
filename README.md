# asr-work-mini
For my son, do asr and nlu annotation works.

## 添加波形显示功能

1. 自动播放
2. 循环播放
3. 显示波形




- [安装`pyaudio`](https://i.stack.imgur.com/Xn0bm.png)
  - `Windows`
    ```shell
    brew install portaudio
    python -m pip install --global-option='build_ext' --global-option='-I/opt/homebrew/Cellar/portaudio/19.7.0/include' --global-option='-L/opt/homebrew/Cellar/portaudio/19.7.0/lib' pyaudio
    ```
  - `Macbook`
    ```shell
    export LDFLAGS="-L/opt/homebrew/opt/mysql-client/lib -L/opt/homebrew/lib"
    export CPPFLAGS="-I/opt/homebrew/opt/mysql-client/include -I/opt/homebrew/include"
    ```
  

- [ ] 界面调整；

- [ ] 上一首下一首；
- [ ] 选定某一个语音；
- [ ] 波形播放进度；
- [x] 播放与暂停；
- [ ] 循环播放；
- [x] 波形背景图虚化；
- [ ] 代码重构
  - [ ] 把大块的组件单独模块化；
  - [ ] 与界面无关的处理程序单独处理；
  - [ ] `QThread`相关的都挪出来；
  - [ ] 添加日志功能；
