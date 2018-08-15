
SET statement_timeout = 0;
SET lock_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;

--
-- Name: pointofsale; Type: SCHEMA; Schema: -; Owner: -
--

CREATE SCHEMA pointofsale;

--
-- Name: plpgsql; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS plpgsql WITH SCHEMA pg_catalog;

SET default_tablespace = '';

SET default_with_oids = false;

--
-- **** Schema: public ****
--

SET search_path = public, pg_catalog;

--
-- Name: settings; Type: TABLE; Schema: -; Owner: -; Tablespace: -
--

CREATE TABLE settings (
    id integer NOT NULL,
    key character varying,
    value integer
);

--
-- Name: settings_id_seq; Type: SEQUENCE; Schema: -; Owner: -
--

CREATE SEQUENCE settings_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

--
-- Name: settings_id_seq; Type: SEQUENCE OWNED BY; Schema: -; Owner: -
--

ALTER SEQUENCE settings_id_seq OWNED BY settings.id;

--
-- Name: id; Type: DEFAULT; Schema: -; Owner: -
--

ALTER TABLE ONLY settings ALTER COLUMN id SET DEFAULT nextval('settings_id_seq'::regclass);

--
-- Name: settings_pkey; Type: CONSTRAINT; Schema: -; Owner: -; Tablespace: -
--

ALTER TABLE ONLY settings
    ADD CONSTRAINT settings_pkey PRIMARY KEY (id);

--
-- **** Schema: pointofsale ****
--

SET search_path = pointofsale, pg_catalog;

--
-- Name: orders; Type: TABLE; Schema: pointofsale; Owner: -; Tablespace: -
--

CREATE TABLE orders (
    id integer NOT NULL,
    description character varying(255)
);

--
-- Name: orders_id_seq; Type: SEQUENCE; Schema: pointofsale; Owner: -
--

CREATE SEQUENCE orders_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

--
-- Name: orders_id_seq; Type: SEQUENCE OWNED BY; Schema: pointofsale; Owner: -
--

ALTER SEQUENCE orders_id_seq OWNED BY orders.id;

--
-- Name: id; Type: DEFAULT; Schema: pointofsale; Owner: -
--

ALTER TABLE ONLY orders ALTER COLUMN id SET DEFAULT nextval('orders_id_seq'::regclass);

--
-- Name: orders_pkey; Type: CONSTRAINT; Schema: pointofsale; Owner: -; Tablespace: -
--

ALTER TABLE ONLY orders
    ADD CONSTRAINT orders_pkey PRIMARY KEY (id);

--
-- **** Schema: - ****
--

SET search_path = "$user", public;
