# Environments

```
Python 3.10.11
Sqlite3 3.44.0
```

# Install Packages Steps;

1. Create python virtual env. Example doc: https://www.freecodecamp.org/news/how-to-setup-virtual-environments-in-python/
2. Activate python virtual env.
    ```shell
    cd <project-name>
    source <venv>/bin/activate
    ```
3. install python packages.
    ```shell
    sudo pip install -r requirements.txt
    ```
4. create database
    ```shell
    python manage.py createDb
    ```
5. database init
    ```shell
    python manage.py dbInit
    ```
6. run on Development env
    ```shell
    python manage.py dev
    ```

7. test on your terminal ...
   <img width="1141" alt="Screenshot 2023-11-12 at 8 51 55 PM" src="https://github.com/thongtran8197/trade-flask/assets/35077609/73ce67c0-147d-46d2-8f4a-e4e7256b8744"> 
     


## When install the necessary packages, some errors maybe happen.

Please check belows to fix the errors.

1. ReadTimeoutError: HTTPSConnectionPool(host='pypi.python.org', port=443): Read time out.

   You can fix this error by using command below.

   `sudo pip install --default-timeout=100 future`

2. Error: Microsoft Visual C++ 14.0 or greater is required. Get it with "Microsoft C++ Build Tools": https://visualstudio.microsoft.com/visual-cpp-build-tools/ 
   
   To fix this error, you should download the visual-cpp-build-tools and install that.

