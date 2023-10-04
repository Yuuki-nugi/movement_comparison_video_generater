# movement_comparison_video_generater
![スクリーンショット 2023-10-04 21 35 01](https://github.com/Yuuki-nugi/movement_comparison_video_generater/assets/61080302/26c987bd-4fb8-41cf-a54f-e271f48f4c0b)
<br><br>
![スクリーンショット 2023-10-04 21 36 17](https://github.com/Yuuki-nugi/movement_comparison_video_generater/assets/61080302/a8b5b8f3-e014-4a95-a98a-ab4710228bbf)

## 機能

### 動画の姿勢推定
- 選択した動画から姿勢（ボーン）を推定します。
- 推定されたボーンが描画された動画とボーンの情報がCSV形式で出力されます。
- 出力されたデータは`/exported`ディレクトリ内に保存されます。
<br><br>

### ボーンの重ね描画
- 片方の動画に2つの動画から得られたボーンを重ねて描画することができます。
- 重ねるフレーム、重ねる身体部位、それぞれのボーンの色などを指定できます。
<br><br>

### グラフ化機能
- 2つの動作における各身体部位の座標変化をグラフ化できます。
- 3つの身体部位がなす角度を計算し、その変化をグラフ化できます。
<br><br>

## クイックスタート

以下のコマンドでツールを起動できます。

```bash
python main.py
```
<br><br>

## コントリビューション
バグの報告や機能の提案など、フィードバックはいつでも歓迎します！
<br><br>

## ライセンス
