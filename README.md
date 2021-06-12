# FunctionalTopology
3Dモデルを解析し，3Dプリントに関する情報を計算します．

## ライブラリ
このレポジトリでは以下のライブラリを使用しています．
* [vedo](https://github.com/marcomusy/vedo)
* [pygalmesh](https://github.com/nschloe/pygalmesh)
* [open3d](https://github.com/intel-isl/Open3D)

以上のライプラリを含む環境は，dockerコンテナとしてまとめてあります．

## インストール
### Step 0
以下を参考にdocker環境を構築します．

[Get Docker (docker docs)](https://docs.docker.com/engine/reference/commandline/push/)

windowsの場合，WSL2をベースエンジンに使用することをお勧めします．
### Step 1
このレポジトリをクローンします．
~~~
git clone https://github.com/Naruki-Ichihara/FunctionalTopology.git && cd FunctionalTopology/.dev
~~~
### Step 2
docker-composeを使用して，[docker image](https://hub.docker.com/repository/docker/ichiharanaruki/functionaltopology)からイメージをビルドします．
~~~
docker-compose up
~~~



