
SET statement_timeout = 0;
SET lock_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;

--
-- Name: plpgsql; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS plpgsql WITH SCHEMA pg_catalog;

SET default_tablespace = '';

SET default_with_oids = false;

--
-- Name: order__c; Type: TABLE; Schema: -; Owner: -; Tablespace: 
--


CREATE TABLE order__c (
    id integer NOT NULL,
    sfid character varying(18),
    description character varying(255)
);

--
-- Name: order__c_id_seq; Type: SEQUENCE; Schema: -; Owner: -
--

CREATE SEQUENCE order__c_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

--
-- Name: order__c_id_seq; Type: SEQUENCE OWNED BY; Schema: -; Owner: -
--

ALTER SEQUENCE order__c_id_seq OWNED BY order__c.id;

--
-- Name: id; Type: DEFAULT; Schema: -; Owner: -
--

ALTER TABLE ONLY order__c ALTER COLUMN id SET DEFAULT nextval('order__c_id_seq'::regclass);

--
-- Name: order__c_pkey; Type: CONSTRAINT; Schema: -; Owner: -; Tablespace: 
--

ALTER TABLE ONLY order__c
    ADD CONSTRAINT order__c_pkey PRIMARY KEY (id);
