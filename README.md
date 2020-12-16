# Twitch Speech
Прототип веб сервиса для распознавания речи и визуализации текста русскоязычных стримеров.

Зачетная работа по курсу "Основы Grid и Cloud вычислений. Часть 1", СпбГУ, 2020г.
## Инструкция по запуску:
* Склонируйте данный репозиторий. Для клонирования сабмодуля:
    * ```
      cd speech_to_text_russian
      git submodule init
      git submodule update
      ```
* Выполните инструкции, указанные в репозитории сабмодуля, а именно:
    * Установите [kaldi](https://kaldi-asr.org/doc/tutorial_setup.html)
    * Установить необходимые Python-библиотеки:
    ```pip install -r requirements.txt```
    * Установить pykaldi: 
    ```
    conda install -c pykaldi pykaldi
    или  
    conda install -c pykaldi pykaldi-cpu
    ```
    * Добавить в PATH пути к компонентам kaldi:
    * Отредактировать файл `model/conf/ivector_extractor.conf`, указав в нем корректные директории
    * Обратите внимание, что размер файла `HCLG.fst` составляет более 500МБ, поэтому его нужно скачать и заменить вручную
* Установить необходимые Python-библиотеки для основного проекта:
  ```
    pip install -r requirements.txt
  ```
* Установить и запустить [mongodb](https://docs.mongodb.com/manual/tutorial/)
* В файл `config.py` в писать желаемые пути до файлов
* Для веб интерфейса:
    * Должны быть установлены flask и flask_cors
    * Должны быть установлены node.js и npm: 
	https://nodejs.org/en/
    * Должны быть установлены все зависимости, для этого нужно перейти в папку twitch_speech/ui и выполнить:
      	npm ci
Для запуска приложения нужно сделать следующее, так же находясь в twitch_speech/ui:
1. Запустить сервер flask. Для этого выполнить 
        export FLASK_APP="server.py"
	flask run
2. Выполнить 
	npm run dev 
Стартовая страница проекта находится по адресу:
	http://localhost:1234/index.html



	

