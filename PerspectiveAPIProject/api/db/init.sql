-- init.sql : Schema and table for Feedback API

CREATE SCHEMA IF NOT EXISTS recsui;

CREATE TABLE IF NOT EXISTS recsui.recsFeedback (
    id SERIAL PRIMARY KEY,
    user_gpn VARCHAR(255) UNIQUE NOT NULL,
    user_name VARCHAR(255) NOT NULL,
    user_email VARCHAR(255) NOT NULL,
    user_feedbacks JSONB DEFAULT '[]'::JSONB,
    updated_time TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
