deploy:
	cp .env.template .env
	make up

restart:
	make down
	make up

down:
	docker compose -f docker-compose.yml down --remove-orphans

up:
	docker compose -f docker-compose.yml up --build --remove-orphans


pep-test:
	poetry --directory ./backend run pylint -j 0 --rcfile ./backend/.pylintrc backend
