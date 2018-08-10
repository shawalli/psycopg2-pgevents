
SET statement_timeout = 0;
SET lock_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;

--
-- Name: salesforce; Type: SCHEMA; Schema: -; Owner: -
--

CREATE SCHEMA salesforce;

--
-- Name: plpgsql; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS plpgsql WITH SCHEMA pg_catalog;

SET default_tablespace = '';

SET default_with_oids = false;

SET search_path = salesforce, pg_catalog;

--
-- Name: order__c; Type: TABLE; Schema: salesforce; Owner: -; Tablespace: -
--


CREATE TABLE order__c (
    id integer NOT NULL,
    sfid character varying(18),
    description character varying(255)
);

--
-- Name: order__c_id_seq; Type: SEQUENCE; Schema: salesforce; Owner: -
--

CREATE SEQUENCE order__c_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

--
-- Name: order__c_id_seq; Type: SEQUENCE OWNED BY; Schema: salesforce; Owner: -
--

ALTER SEQUENCE order__c_id_seq OWNED BY order__c.id;

--
-- Name: id; Type: DEFAULT; Schema: salesforce; Owner: -
--

ALTER TABLE ONLY order__c ALTER COLUMN id SET DEFAULT nextval('order__c_id_seq'::regclass);

--
-- Name: order__c_pkey; Type: CONSTRAINT; Schema: salesforce; Owner: -; Tablespace: -
--

ALTER TABLE ONLY order__c
    ADD CONSTRAINT order__c_pkey PRIMARY KEY (id);
