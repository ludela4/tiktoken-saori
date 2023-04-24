# tikitoken-saori
tikitokenのSAORIラッパー

## 各種メソッド

### num_tokens_from_messages
メッセージのトークン数を数える関数

引数1: メソッド
num_tokens_from_messages
引数2: messages
chatGPTで送信するmessagesのjsonの文字列。


### elim_tokens_to_num
入力したトークン数になるまでメッセージの配列からメッセージを消去し、残ったものを返す。

引数1: メソッド名
num_tokens_from_messages
引数2: messages
chatGPTで送信するmessagesのjsonの文字列。
引数3: num

