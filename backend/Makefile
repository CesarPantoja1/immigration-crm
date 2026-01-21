.PHONY: help install migrate run test behave shell clean docker-up docker-down

help:
	@echo "Comandos disponibles:"
	@echo "  make install       - Instalar dependencias"
	@echo "  make migrate       - Ejecutar migraciones"
	@echo "  make run           - Ejecutar servidor de desarrollo"
	@echo "  make test          - Ejecutar todos los tests"
	@echo "  make behave        - Ejecutar tests BDD con Behave"
	@echo "  make shell         - Abrir shell de Django"
	@echo "  make clean         - Limpiar archivos temporales"
	@echo "  make docker-up     - Levantar contenedores Docker"
	@echo "  make docker-down   - Detener contenedores Docker"

install:
	pip install -r requirements.txt

migrate:
	python manage.py makemigrations
	python manage.py migrate

run:
	python manage.py runserver

test:
	pytest
	behave

behave:
	behave features/

pytest:
	pytest

shell:
	python manage.py shell

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f

createsuperuser:
	python manage.py createsuperuser

collectstatic:
	python manage.py collectstatic --noinput
