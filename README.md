# LLMs_Chat
A chat application that freely switches between multiple LLMs deployed on Azure OpenAI

## 開発時確認（分離後セットで確認）
CSS/HTML/JS を assets と lib の loader で分離しているため、アセットや loader を変更したあとは、次で全 loader が正常に読み込めることを確認するとよい。

```bash
python verify_loaders.py
```
