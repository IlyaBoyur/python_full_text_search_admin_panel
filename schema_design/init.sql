DROP DATABASE IF EXISTS movies;
CREATE DATABASE movies;
\c movies;
-- Создаём отдельную схему для контента, чтобы ничего не перемешалось с сущностями Django
CREATE SCHEMA IF NOT EXISTS content;
-- Обновить поиска таблиц
SET search_path TO content,public;
-- Жанры, которые могут быть у кинопроизведений
CREATE TABLE IF NOT EXISTS content.genre (
    id uuid PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    created_at timestamp with time zone,
    updated_at timestamp with time zone
);
-- Убраны актёры, жанры, режиссёры и сценаристы, так как они находятся с этой таблицей в отношении m2m
CREATE TABLE IF NOT EXISTS content.film_work (
    id uuid PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    creation_date DATE,
    certificate TEXT NOT NULL,
    file_path TEXT NOT NULL,
    rating FLOAT,
    type TEXT  NOT NULL,
    created_at timestamp with time zone,
    updated_at timestamp with time zone
);
-- Обобщение для актёра, режиссёра и сценариста
CREATE TABLE IF NOT EXISTS content.person (
    id uuid PRIMARY KEY,
    full_name TEXT NOT NULL,
    birth_date DATE,
    created_at timestamp with time zone,
    updated_at timestamp with time zone
);
-- m2m-таблица для связывания кинопроизведений с жанрами
CREATE TABLE IF NOT EXISTS content.genre_film_work (
    id uuid PRIMARY KEY,
    film_work_id uuid NOT NULL,
    genre_id uuid NOT NULL,
    created_at timestamp with time zone
);
-- Обязательно проверяется уникальность жанра и кинопроизведения, чтобы не появлялось дублей
CREATE UNIQUE INDEX IF NOT EXISTS film_work_genre
ON content.genre_film_work(film_work_id, genre_id);
-- m2m-таблица для связывания кинопроизведений с участниками
CREATE TABLE IF NOT EXISTS content.person_film_work (
    id uuid PRIMARY KEY,
    film_work_id uuid NOT NULL,
    person_id uuid NOT NULL,
    role TEXT NOT NULL,
    created_at timestamp with time zone
);
-- Обязательно проверяется уникальность кинопроизведения, человека и роли человека, чтобы не появлялось дублей
-- Один человек может быть сразу в нескольких ролях (например, сценарист и режиссёр)
CREATE UNIQUE INDEX IF NOT EXISTS film_work_person_role
ON content.person_film_work (film_work_id, person_id, role);
