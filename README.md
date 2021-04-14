# iTurmas

## Initial setup

* Download, install and setup `docker-ce` following instructions on the [Docker](https://docs.docker.com/get-docker/) website.
* Install `docker-compose` as described [here](https://docs.docker.com/compose/install/).
* Clone the project [repository](https://gitlab.com/danielmmartin/iturmas.git):
 
```shell script
git clone https://gitlab.com/danielmmartin/iturmas.git
```

Note: you need to be a collaborator and git will ask for your Gitlab credentials.

* In a terminal, navigate to the project root folder and create a `./driver/bin` sub-folder:

```shell script
mkdir ./driver/bin
```
* Place the scheduler binary file inside `./driver/bin` and rename it `match`.
* Don't forget to make it executable:

```shell script
chmod +x ./driver/bin/match
```
* In the project root folder, build the docker image for the project:

```shell script
docker build -t iturmas .
```

* Create a `data` folder inside the project root folder.
* Create a `mysql` folder inside the project root folder.

* In the root folder of this project, create a `.env` file with the following content:

```dotenv
MYSQL_ROOT_HOST=%
MYSQL_ROOT_PASSWORD=<fill_it_in>
MYSQL_USER=python
MYSQL_PASSWORD=<fill_it_in>
MYSQL_DATABASE=iturmas
MYSQL_INITDB_SKIP_TZINFO=true
SECRET_KEY=<fill_it_in>
ABSOLUTE_DATA_SUBDIR=/data
ADMIN_PASSWORD=<fill_it_in>
```

Note: don't forget to fill in the blanks with your preferred secrets.

Warning: do not use spaces or quotation marks in any of the secrets, and do not put them in quotes of any kind!

* Now, either set variables `MAIL_SERVER` and `MAIL_PORT` in the `.env` file above to point to a real smtp server or 
leave them undefined to use the testing mail server.

Note: from this moment you could choose to run `docker-compose up` and the app would be up and running, but... 
there are some instabilities with this method as the database connection keeps being aborted from time to time.
So, if the app becomes unresponsive, we suggest you follow along the longer path that is proven to work, 
which we describe next.

* Fire up a clean MariaDB container with docker using the following command:

```shell script
docker run -d --name mariadb_server -p 3306:3306 -v $(pwd)/mysql:/var/lib/mysql --env-file .env mariadb:10.3
```

Note: you can change the folder `$(pwd)/mysql` to whatever place you want to store the database in the host machine, 
it needs to be an absolute path.

* Fire up a clean Redis container with docker:

```shell script
docker run -d --name redis_server -p 6379:6379 redis:6.0
```

* Fire up the Redis queue worker contained in the project:

```shell script
docker run -d --name worker --network host -v $(pwd)/data:/data --env-file .env iturmas python worker.py
```

Note: this worker is responsible for executing tasks in the background (to avoid blocking the server).

* If you decided to use leave `MAIL_SERVER` and `MAIL_PORT` undefined in the `.env` file it is time to launch 
a testing mail server on `localhost:8025` to check whether your application is sending e-mails correctly. 
Using a separate terminal type:

```shell script
docker run -it --name mail_server --network host iturmas python -m smtpd -n -c DebuggingServer localhost:8025
``` 

Note: we asked you to use a separate terminal because the command above will block the terminal and print 
there all emails sent by the app.

* Finally, fire up the main web server:

```shell script
docker run -it --name web --network host -v $(pwd)/data:/data --env-file .env iturmas
```

## Running it after the initial setup

Now that you have docker setup and running all the necessary images installed, if you want to run the app a second time,
you do not need to repeat all the steps above. Simply start all the containers that were created in the setup above:

```shell script
docker container start web worker mail_server redis_server mariadb_server
```

Note: although a docker-compose.yml file is available, the database connection keeps dropping 
and causes delays in the app if one uses `docker-compose up`. So we encourage you to follow the steps 
above until we fix the cause of the instability of the app with docker-compose.

## Updating the app

Once there is a new version of the app, you must do some extra work before having the latest version running. 

* First cleanup running containers. If you used `docker-compose`, run: 

```shell script
docker-compose rm -v   
```

Otherwise, run 

```shell script
docker container stop web worker mail_server
docker container rm web worker mail_server
```

* Now update your local git repo:

```shell script
git pull
```

* Rebuild the docker image:

```shell script
docker build -t iturmas .
```

* Either run `docker-compose up` or if you used the longer set of instructions, rerun the last three lines 
to instantiate containers `worker`, `mail_server` and `web` respectively.

## TODO:

* find out what the problem is with docker-compose and the connection drops between the app and mariadb.
* create the concept of REQUIRED PROPERTIES for models
* validation for the properties field (json parsing, required properties) on CSV for domain import
* validation (required parameters / properties) before executing scheduler
* Use DATABASE_DANGER_PASSWORD instead of the current hash variable
* test  