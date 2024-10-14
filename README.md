# IIDX Notes Analyzer

弐寺の譜面を分析するためのツールです。\
[TexTage](https://textage.cc)から譜面データをスクレイピングしています。

## 合法性

以下を確認し、法的に問題が無いことを確認しています。\
問題があればissueからの報告をお願いします。

- 利用規約
    - 読んだ結果、問題なさそう
- robots.txt
    - 見つからないのでなさそう
- その他一般的な規範
    - 連続アクセス時は間隔を1秒以上空けるつもり
        - このツール自体をありえない速度で何度も起動したりしないようお願いします

## 起動の仕方

まだインストーラー等に固めるつもりはないので、開発者用の実行方法しかありません。\
開発環境の作成を含む感じになってくるので、少し込み入った手順になります。

※ Macでのみ起動確認をしています。Windowsではターミナルに入力するコマンド等が微妙に異なってくると思いますが、その辺は自身で解決をお願いします。

### 1. Pythonをインストール

### 2. 仮想環境の作成

このツールは他者が作ったライブラリを利用します。\
この際、他のプログラムも使用するようなグローバルな領域にライブラリをダウンロードして使用すると、他のプログラムが勝手にライブラリをアップデートして、その結果こちらのプログラムがバグる、というような事態が発生します。\
そのため、ライブラリのダウンロード先をローカルな場所に設定すると共に、本ツール使用時はそこのライブラリしか使用しないような設定を行います。\
これが仮想化です。\
めんどかったらやらなくてもいいです。

```console
# 本ツールのあるフォルダ上で実行してください。
# 成功すると、本ツールのあるフォルダの直下に`.venv`フォルダが作成されます。
python -m venv .venv
```

以降、pythonを呼び出す時は`.venv/bin/python`の方を呼び出す必要があります。\
これをいちいち打ち込むのはめんどくさいですが、以下のアクティベーションを行うことで、`.venv/bin`フォルダにパスが通るようになり、単に`python`と打ち込んでもこちらのpythonを呼び出すことができるようになります。

```console
# 本ツールのあるフォルダ上で実行してください。
# シェルやOSの種類によって呼ぶプログラムが変わってきます。詳しくは調べてください。
source .venv/bin/activate
```

アクティベーションの効果はターミナルを閉じた際に自動で終了すると思いますが、手動で終了したい場合は以下のアクティベーション解除を行う必要があります。

```console
# `.venv/bin`にパスが通っているため、これだけで呼べます。
deactivate
```

### 3. ライブラリのダウンロード

```console
# 本ツールのあるフォルダ上で実行してください。
python -m pip install -r requirements.txt
```

### 4. 本ツールが使用するブラウザエンジンのインストール

```console
playwright install chromium
```

仮想環境を用意しようと関係なく、ブラウザエンジンはグローバルにインストールされます。残念。

### 5. `scrape_music_list`を実行

ようやくプログラムの実行です。\
まずは`scrape_music_list`を実行することで、TexTageから楽曲一覧をスクレイピングしてきます。

```console
# 本ツールのあるフォルダ上で実行してください。
python -m iidx_notes_analyzer scrape_music_list
```

取ってきたデータは本ツールがあるフォルダ直下の`data`フォルダ下に保存されます。\
サイトに何度もアクセスするのも迷惑になるので、一度データを保存し、後は保存後のデータをわちゃわちゃ解析しまくる方針としています。

一度保存したデータを再度更新したい場合、以下のように上書きオプションをオンにすると良いです。\
上書きオプションがオフのままだと、保存先のファイルが既に存在するためエラーとなります。\
ただし、誤って関係ないファイルを上書きしてしまうのが怖いので、初回実行時はオフのままにしておくのがオススメです。

```console
# 本ツールのあるフォルダ上で実行してください。
python -m iidx_notes_analyzer scrape_music_list --overwrite
```

### 6. `scrape_score`を実行

次に`scrape_score`を実行することで、曲毎に譜面データをスクレイピングしてきます。\
対象曲のリストアップに、上で保存した楽曲一覧を使用します。

```console
# 本ツールのあるフォルダ上で実行してください。
# AC全曲を一気に（非常に時間がかかるので、条件を絞る方がオススメ）
python -m iidx_notes_analyzer scrape_score
# SPのみ
python -m iidx_notes_analyzer scrape_score SP
# SPかつIIDX REDのみ
python -m iidx_notes_analyzer scrape_score SP 11
# SPかつIIDX RED以降全て
python -m iidx_notes_analyzer scrape_score SP 11-
# SPかつIIDX REDからIIDX GOLDまで
python -m iidx_notes_analyzer scrape_score SP 11-14
# SPかつAAのみ（曲に対応するIDはTexTageのURLを元に自分で調べてください）
python -m iidx_notes_analyzer scrape_score SP 11 aa_amuro
# AA(SPA)のみ
python -m iidx_notes_analyzer scrape_score SP 11 aa_amuro A
# 全曲のDPAのみ
python -m iidx_notes_analyzer scrape_score DP '' '' A
```

なお、substreamは`sub`です。\
また、難易度はB, N, H, A, Lの5種類です。

譜面データは`data/notes`フォルダに保存されます。
一度保存した譜面は次は保存対象外となるので、再度保存し直したい譜面がある場合は既存の譜面データを削除してください。

### 7. `analyze`を実行

```console
# 本ツールのあるフォルダ上で実行してください。
python -m iidx_notes_analyzer analyze
# 実際に出てこない同時押しパターンも含め、全てのパターンを表示したい時
python -m iidx_notes_analyzer analyze --show-all
# ヒットした曲（譜面）が何か確認したい時
python -m iidx_notes_analyzer analyze --list
# SPのみ
python -m iidx_notes_analyzer analyze --mode=SP
# SPかつIIDX REDのみ
python -m iidx_notes_analyzer analyze --mode=SP --ver=11
# SPかつIIDX RED以降全て
python -m iidx_notes_analyzer analyze --mode=SP --ver=11-
# SPかつIIDX REDからIIDX GOLDまで
python -m iidx_notes_analyzer analyze --mode=SP --ver=11-14
# SPかつAAのみ（曲に対応するIDはTexTageのURLを元に自分で調べてください）
python -m iidx_notes_analyzer analyze --mode=SP --tag=aa_amuro
# AA(SPA)のみ
python -m iidx_notes_analyzer analyze --mode=SP --tag=aa_amuro --diff=A
# 全曲のDPAのみ
python -m iidx_notes_analyzer analyze --mode=DP --diff=A
```

譜面データが保存された曲の内、指定された条件に当てはまる曲を対象にして分析し、
結果（全ての同時押しパターンの個数）を表示します。

今のところ、DP譜面の集計とかするとカス（プレイサイドのことを考えてない）です。

## 実行結果

5thのSPA譜面のみを集めてみます。

```console
python -m iidx_notes_analyzer scrape_music_list
python -m iidx_notes_analyzer scrape_score SP 5 '' A
```

```console
Found 16 scores.
Scraping 1/16 SP VER:5 [abyss] Abyss (A) ...finished.
Scraping 2/16 SP VER:5 [inmyeyes] in my eyes (A) ...finished.
Scraping 3/16 SP VER:5 [loveage] LOVE AGAIN TONIGHT～for Mellisa mix～ (A) ...finished.
Scraping 4/16 SP VER:5 [outwall] outer wall (A) ...finished.
Scraping 5/16 SP VER:5 [qqq] QQQ (A) ...finished.
Scraping 6/16 SP VER:5 [radical] Radical Faith (A) ...finished.
Scraping 7/16 SP VER:5 [real] Real (A) ...finished.
Scraping 8/16 SP VER:5 [regulus] Regulus (A) ...finished.
Scraping 9/16 SP VER:5 [rideon] RIDE ON THE LIGHT(HI GREAT MIX) (A) ...finished.
Scraping 10/16 SP VER:5 [sometm27] sometime (A) ...finished.
Scraping 11/16 SP VER:5 [spin] Spin the disc (A) ...finished.
Scraping 12/16 SP VER:5 [stheart] STILL IN MY HEART (A) ...finished.
Scraping 13/16 SP VER:5 [sync] sync (A) ...finished.
Scraping 14/16 SP VER:5 [thecube] THE CUBE (A) ...finished.
Scraping 15/16 SP VER:5 [tpola_17] THE SHINING POLARIS (A) ...finished.
Scraping 16/16 SP VER:5 [v_taka] V (A) ...finished.
```

解析を実行します。

```console
python -m iidx_notes_analyzer analyze
```

```console
Found 16 scores.
 |______:1096
 _|_____:777
 __|____:1029
 ___|___:890
 ____|__:1051
 _____|_:784
 ______|:732
 ||_____:50
 |_|____:257
 |__|___:189
 |___|__:260
 |____|_:256
 |_____|:316
 _||____:12
 _|_|___:77
 _|__|__:55
 _|___|_:60
 _|____|:100
 __||___:22
 __|_|__:159
 __|__|_:80
 __|___|:125
 ___||__:37
 ___|_|_:50
 ___|__|:48
 ____||_:23
 ____|_|:100
 _____||:12
 |||____:3
 ||_|___:11
 ||__|__:9
 ||___|_:25
 ||____|:37
 |_|_|__:44
 |_|__|_:29
 |_|___|:52
 |__||__:8
 |__|_|_:23
 |__|__|:19
 |___||_:8
 |___|_|:33
 |____||:6
 _||_|__:2
 _|_|_|_:36
 _|_|__|:4
 _|__||_:1
 _|__|_|:1
 __|||__:2
 __||_|_:4
 __|_||_:1
 __|_|_|:33
 __|__||:4
 ||_|_|_:1
 ||___||:5
 |_||_|_:1
 |_||__|:1
 |_|_|_|:42
S|______:50
S_|_____:36
S__|____:53
S___|___:34
S____|__:33
S_____|_:32
S______|:40
S||_____:2
S|_|____:32
S|__|___:19
S|___|__:26
S|____|_:11
S|_____|:40
S_||____:1
S_|_|___:4
S_|__|__:5
S_|___|_:2
S_|____|:16
S__||___:3
S__|_|__:2
S__|__|_:5
S__|___|:12
S___|_|_:6
S___|__|:6
S____||_:1
S____|_|:11
S_____||:1
S|||____:2
S||_|___:3
S||__|__:3
S||___|_:2
S||____|:2
S|_|_|__:5
S|_|__|_:9
S|_|___|:16
S|__||__:3
S|__|_|_:7
S|__|__|:6
S|___||_:3
S|___|_|:15
S_|_|_|_:4
S_|_|__|:1
S_|__|_|:1
S__|_|_|:8
S|_||__|:1
S|_|_|_|:4
S__||_||:2
S|_||_||:1
```
