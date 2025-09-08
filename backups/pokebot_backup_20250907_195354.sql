--
-- PostgreSQL database dump
--

\restrict HlUdAdIlvNJ0o6DqMZZHTcixQ6uSA3jRzOPSEkv7shSnt4iDH29kvMpYjcfA5sJ

-- Dumped from database version 17.6
-- Dumped by pg_dump version 17.6

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: battles; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.battles (
    id integer NOT NULL,
    challenger_id bigint,
    opponent_id bigint,
    challenger_pokemon integer,
    opponent_pokemon integer,
    turn_user_id bigint,
    battle_data jsonb,
    status character varying(10) DEFAULT 'active'::character varying,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.battles OWNER TO postgres;

--
-- Name: battles_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.battles_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.battles_id_seq OWNER TO postgres;

--
-- Name: battles_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.battles_id_seq OWNED BY public.battles.id;


--
-- Name: npc_completions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.npc_completions (
    user_id bigint NOT NULL,
    npc_type integer NOT NULL,
    npc_index integer NOT NULL,
    completed_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.npc_completions OWNER TO postgres;

--
-- Name: pokemon; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.pokemon (
    id integer NOT NULL,
    owner_id bigint,
    species_id integer,
    level integer DEFAULT 5,
    experience integer DEFAULT 0,
    hp_iv integer DEFAULT 0,
    attack_iv integer DEFAULT 0,
    defense_iv integer DEFAULT 0,
    special_iv integer DEFAULT 0,
    speed_iv integer DEFAULT 0,
    current_hp integer,
    is_shiny boolean DEFAULT false,
    in_party boolean DEFAULT false,
    party_position integer,
    move1 character varying(20),
    move2 character varying(20),
    move3 character varying(20),
    move4 character varying(20),
    status_condition character varying(10),
    caught_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.pokemon OWNER TO postgres;

--
-- Name: pokemon_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.pokemon_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.pokemon_id_seq OWNER TO postgres;

--
-- Name: pokemon_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.pokemon_id_seq OWNED BY public.pokemon.id;


--
-- Name: pokemon_species; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.pokemon_species (
    id integer NOT NULL,
    name character varying(20) NOT NULL,
    type1 character varying(10) NOT NULL,
    type2 character varying(10),
    base_hp integer NOT NULL,
    base_attack integer NOT NULL,
    base_defense integer NOT NULL,
    base_special integer NOT NULL,
    base_speed integer NOT NULL,
    exp_group character varying(20) NOT NULL,
    rarity character varying(10) NOT NULL
);


ALTER TABLE public.pokemon_species OWNER TO postgres;

--
-- Name: server_config; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.server_config (
    guild_id bigint NOT NULL,
    spawn_channels bigint[],
    message_count integer DEFAULT 0,
    messages_until_spawn integer DEFAULT 15
);


ALTER TABLE public.server_config OWNER TO postgres;

--
-- Name: trades; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.trades (
    id integer NOT NULL,
    requester_id bigint,
    target_id bigint,
    pokemon_offered integer,
    pokemon_requested integer,
    status character varying(10) DEFAULT 'pending'::character varying,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    expires_at timestamp without time zone DEFAULT (CURRENT_TIMESTAMP + '00:05:00'::interval)
);


ALTER TABLE public.trades OWNER TO postgres;

--
-- Name: trades_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.trades_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.trades_id_seq OWNER TO postgres;

--
-- Name: trades_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.trades_id_seq OWNED BY public.trades.id;


--
-- Name: user_inventory; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.user_inventory (
    user_id bigint NOT NULL,
    item_name character varying(30) NOT NULL,
    quantity integer DEFAULT 0
);


ALTER TABLE public.user_inventory OWNER TO postgres;

--
-- Name: users; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.users (
    user_id bigint NOT NULL,
    username character varying(32) NOT NULL,
    money integer DEFAULT 5000,
    badges integer DEFAULT 0,
    default_pokeball character varying(20) DEFAULT 'pokeball'::character varying,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.users OWNER TO postgres;

--
-- Name: battles id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.battles ALTER COLUMN id SET DEFAULT nextval('public.battles_id_seq'::regclass);


--
-- Name: pokemon id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.pokemon ALTER COLUMN id SET DEFAULT nextval('public.pokemon_id_seq'::regclass);


--
-- Name: trades id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.trades ALTER COLUMN id SET DEFAULT nextval('public.trades_id_seq'::regclass);


--
-- Data for Name: battles; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.battles (id, challenger_id, opponent_id, challenger_pokemon, opponent_pokemon, turn_user_id, battle_data, status, created_at) FROM stdin;
3	272439835694727170	408190648924110858	15	10	272439835694727170	{}	completed	2025-08-29 04:24:11.89066
4	408190648924110858	272439835694727170	5	15	408190648924110858	{}	completed	2025-08-29 04:32:38.636655
7	408190648924110858	137795731951058944	49	53	408190648924110858	{}	active	2025-08-31 12:23:35.647408
8	408190648924110858	137795731951058944	49	53	408190648924110858	{}	active	2025-08-31 12:27:04.389835
9	408190648924110858	137795731951058944	49	53	408190648924110858	{}	completed	2025-08-31 12:31:07.79503
12	408190648924110858	741060754660130899	49	26	408190648924110858	{}	completed	2025-08-31 14:52:28.268935
28	408190648924110858	741060754660130899	49	26	408190648924110858	{}	active	2025-09-01 14:04:41.484384
29	408190648924110858	741060754660130899	49	26	408190648924110858	{}	completed	2025-09-01 16:25:29.211448
30	408190648924110858	741060754660130899	5	27	408190648924110858	{}	completed	2025-09-01 16:30:36.194499
31	741060754660130899	408190648924110858	26	5	741060754660130899	{}	completed	2025-09-01 16:32:49.457761
32	408190648924110858	741060754660130899	5	27	408190648924110858	{}	active	2025-09-02 01:18:32.834272
33	408190648924110858	741060754660130899	49	26	408190648924110858	{}	completed	2025-09-02 01:38:32.016418
34	408190648924110858	741060754660130899	5	26	408190648924110858	{}	active	2025-09-02 06:36:43.942399
35	408190648924110858	741060754660130899	5	27	408190648924110858	{}	completed	2025-09-02 06:59:47.005158
36	408190648924110858	741060754660130899	5	26	408190648924110858	{}	active	2025-09-02 07:10:57.527807
37	408190648924110858	741060754660130899	5	27	408190648924110858	{}	active	2025-09-02 07:36:59.884813
\.


--
-- Data for Name: npc_completions; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.npc_completions (user_id, npc_type, npc_index, completed_at) FROM stdin;
408190648924110858	1	0	2025-09-01 13:28:26.27202
\.


--
-- Data for Name: pokemon; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.pokemon (id, owner_id, species_id, level, experience, hp_iv, attack_iv, defense_iv, special_iv, speed_iv, current_hp, is_shiny, in_party, party_position, move1, move2, move3, move4, status_condition, caught_at) FROM stdin;
52	137795731951058944	127	20	7508	2	7	10	13	6	0	f	f	\N	vice_grip	focus_energy	string_shot	tackle	\N	2025-08-31 11:04:57.320561
36	369809123925295104	5	27	15880	9	8	7	2	4	73	f	t	1	scratch	growl	Ember	Leer	\N	2025-08-31 04:25:36.857546
32	408190648924110858	79	23	0	13	11	9	12	1	80	f	f	\N	curse	yawn	water_gun	confusion	\N	2025-08-30 17:26:43.258464
38	1008209186913529857	7	6	1813	8	7	10	9	13	22	f	t	1	tackle	tail_whip	\N	\N	\N	2025-08-31 04:30:23.586145
28	408190648924110858	150	100	0	10	6	11	10	13	342	t	f	\N	confusion	teleport	\N	\N	\N	2025-08-30 15:19:08.688372
73	137795731951058944	44	18	0	4	11	5	15	4	51	f	f	\N	tackle	absorb	razor_leaf	\N	\N	2025-08-31 20:14:28.870654
12	272439835694727170	1	5	125	2	11	12	13	14	19	f	f	\N	tackle	growl	\N	\N	\N	2025-08-29 04:11:07.073452
30	408190648924110858	65	40	109	12	15	15	8	1	0	f	f	\N	confusion	teleport	psybeam	psychic	\N	2025-08-30 15:31:58.527273
51	408190648924110858	124	21	0	8	1	6	0	8	61	f	f	\N	pound	lick	double_slap	tackle	\N	2025-08-31 09:51:43.995727
71	137795731951058944	69	22	287	2	8	7	13	2	54	f	f	\N	wrap	sleep_powder	poison_powder	stun_spore	\N	2025-08-31 19:04:15.714772
53	137795731951058944	94	36	9755	9	2	14	4	13	84	t	t	1	lick	confuse_ray	night_shade	psychic	\N	2025-08-31 11:13:06.907257
40	1008209186913529857	110	20	1620	2	6	8	12	10	27	f	t	2	poison_sting	tackle	acid	sludge	\N	2025-08-31 04:37:09.362368
29	408190648924110858	65	36	0	7	15	8	5	15	90	f	f	\N	confusion	teleport	\N	\N	\N	2025-08-30 15:27:24.447579
49	741060754660130899	151	38	40634	2	11	7	8	15	125	f	f	\N	confusion	dream_eater	psybeam	psychic	\N	2025-08-31 09:13:52.769308
14	272439835694727170	101	28	34	6	10	10	3	0	74	f	f	\N	thundershock	tackle	\N	\N	\N	2025-08-29 04:14:53.149349
45	1145424000953090130	7	5	661	11	4	11	6	12	20	f	t	1	tackle	tail_whip	\N	\N	\N	2025-08-31 09:11:03.850522
7	408190648924110858	62	28	3	10	9	8	7	14	94	f	f	\N	tackle	\N	\N	\N	\N	2025-08-28 17:10:20.559195
11	408190648924110858	64	80	3	8	13	15	9	8	166	f	f	\N	confusion	teleport	\N	\N	\N	2025-08-28 18:23:35.120455
43	408190648924110858	97	100	19399	15	10	2	7	2	310	f	f	\N	confusion	teleport	psybeam	psychic	\N	2025-08-31 07:10:00.882665
13	272439835694727170	41	16	69	1	14	10	3	12	39	f	f	\N	leech_life	supersonic	bite	confuse_ray	\N	2025-08-29 04:12:40.586292
34	408190648924110858	151	39	0	4	5	11	0	6	130	f	f	\N	confusion	teleport	psybeam	psychic	\N	2025-08-30 17:54:03.267218
35	408190648924110858	150	24	0	0	8	15	1	11	84	f	f	\N	confusion	teleport	psybeam	psychic	\N	2025-08-30 17:54:11.911374
58	408190648924110858	12	30	28347	6	9	11	9	8	79	f	t	4	string_shot	harden	Confusion	PoisonPowder	\N	2025-08-31 12:07:51.424743
39	137795731951058944	119	16	2874	3	4	1	7	4	52	f	f	\N	tackle	bubble	surf	\N	\N	2025-08-31 04:31:23.911644
5	408190648924110858	150	100	1361	11	9	9	3	9	344	t	t	3	tackle	razor_wind	\N	\N	\N	2025-08-28 17:00:20.093489
21	272439835694727170	129	7	0	15	11	8	10	10	21	f	f	\N	splash	\N	\N	\N	\N	2025-08-29 04:29:14.599188
22	272439835694727170	129	7	0	9	4	7	13	10	21	f	f	\N	splash	\N	\N	\N	\N	2025-08-29 04:29:16.292559
26	741060754660130899	2	27	16181	1	4	1	4	5	36	f	f	\N	tackle	growl	Leech Seed	vine_whip	\N	2025-08-30 15:05:38.088756
37	137795731951058944	8	23	9930	0	3	10	9	11	75	f	f	\N	tackle	tail_whip	surf	Bubble	\N	2025-08-31 04:30:14.084599
9	408190648924110858	150	80	400	14	5	9	1	8	282	t	f	\N	tackle	\N	\N	\N	\N	2025-08-28 18:18:22.387695
31	408190648924110858	58	12	0	1	4	13	8	9	35	f	f	\N	bite	roar	\N	\N	\N	2025-08-30 17:26:29.775578
41	369809123925295104	20	25	15688	11	0	15	7	3	68	f	t	2	tackle	growl	quick_attack	body_slam	\N	2025-08-31 05:34:31.667141
44	408190648924110858	29	14	0	5	6	3	6	1	40	f	f	\N	scratch	double_kick	\N	\N	\N	2025-08-31 09:01:23.241337
33	408190648924110858	132	100	13911	7	14	9	14	0	220	f	t	5	transform	tackle	growl	quick_attack	\N	2025-08-30 17:27:07.05236
46	1145424000953090130	39	20	661	11	3	5	8	14	80	f	t	2	pound	disable	defense_curl	double_slap	\N	2025-08-31 09:11:17.757315
59	137795731951058944	97	26	0	11	10	3	1	13	85	f	f	\N	confusion	teleport	psybeam	psychic	\N	2025-08-31 12:08:53.763272
15	272439835694727170	133	99	111	11	1	7	2	7	0	t	t	1	quick_attack	bite	focus_energy	take_down	\N	2025-08-29 04:16:12.515938
16	272439835694727170	133	99	100	6	12	1	3	5	229	t	t	2	quick_attack	bite	focus_energy	take_down	\N	2025-08-29 04:16:21.378093
17	272439835694727170	133	99	100	9	9	3	4	8	235	t	t	3	quick_attack	bite	focus_energy	take_down	\N	2025-08-29 04:16:30.032908
55	137795731951058944	29	12	0	14	4	5	14	14	38	f	f	\N	scratch	double_kick	\N	\N	\N	2025-08-31 11:17:31.857195
27	408190648924110858	150	100	100	14	7	3	2	3	350	t	f	\N	confusion	teleport	\N	\N	\N	2025-08-30 15:18:34.735917
10	408190648924110858	63	13	1436	9	10	5	13	5	0	f	f	\N	teleport	kinesis	\N	\N	\N	2025-08-28 18:21:44.025577
20	272439835694727170	133	99	83	10	7	0	14	10	237	t	t	4	quick_attack	bite	focus_energy	take_down	\N	2025-08-29 04:17:04.130122
19	272439835694727170	133	99	83	6	9	3	2	11	229	t	t	5	quick_attack	bite	focus_energy	take_down	\N	2025-08-29 04:16:56.209642
18	272439835694727170	133	99	83	2	4	13	15	0	221	t	t	6	quick_attack	bite	focus_energy	take_down	\N	2025-08-29 04:16:53.450919
54	774175076366024715	8	22	8236	10	6	4	12	1	81	f	t	1	tackle	tail_whip	Bubble	water_gun	\N	2025-08-31 11:17:30.184665
23	408190648924110858	150	96	62478	8	2	9	0	0	324	f	t	2	confusion	teleport	Barrier	Psychic	\N	2025-08-29 11:49:27.697522
60	137795731951058944	57	29	0	1	8	9	2	4	77	f	f	\N	karate_chop	leer	seismic_toss	submission	\N	2025-08-31 12:09:40.032885
4	741060754660130899	150	99	53980	5	7	9	13	12	328	f	f	\N	tackle	strength	\N	\N	\N	2025-08-28 16:58:13.932254
56	137795731951058944	96	13	0	5	0	7	6	8	39	f	f	\N	hypnosis	disable	\N	\N	\N	2025-08-31 11:49:38.072595
61	774175076366024715	12	29	7838	7	10	15	5	2	77	f	t	2	string_shot	tackle	leech_life	pin_missile	\N	2025-08-31 12:18:07.55529
48	408190648924110858	150	20	0	2	10	4	11	7	73	f	f	\N	confusion	teleport	psybeam	psychic	\N	2025-08-31 09:11:41.567484
6	408190648924110858	151	100	513	8	4	14	10	3	326	t	f	\N	tackle	\N	\N	\N	\N	2025-08-28 17:09:26.224504
42	137795731951058944	54	17	4963	6	10	15	10	10	46	f	f	\N	scratch	tail_whip	water_gun	surf	\N	2025-08-31 06:22:39.520207
50	408190648924110858	12	19	12358	4	7	5	5	12	53	f	f	\N	tackle	string_shot	Confusion	PoisonPowder	\N	2025-08-31 09:29:21.692888
47	137795731951058944	39	20	4019	0	6	1	10	5	76	f	f	\N	pound	disable	defense_curl	double_slap	\N	2025-08-31 09:11:17.799097
83	408190648924110858	146	40	0	9	3	13	4	12	129	t	f	\N	fire_spin	peck	ember	tackle	\N	2025-09-05 10:10:07.133865
110	408190648924110858	4	13	0	15	13	9	3	8	37	f	f	\N	scratch	ember	\N	\N	\N	2025-09-06 14:30:48.521319
75	137795731951058944	104	18	0	11	1	9	8	1	49	f	f	\N	tail_whip	bone_club	headbutt	\N	\N	2025-08-31 21:45:49.703859
90	408190648924110858	69	25	0	3	0	8	11	3	61	f	f	\N	wrap	poisonpowder	sleep_powder	stun_spore	\N	2025-09-05 13:13:29.431137
57	137795731951058944	4	22	7597	14	14	2	0	9	55	f	t	2	growl	ember	leer	rage	\N	2025-08-31 12:03:25.109242
120	1008209186913529857	50	25	0	9	1	14	8	0	44	f	t	5	scratch	growl	dig	sand_attack	\N	2025-09-07 07:31:56.175749
117	446408785804656640	16	12	0	14	8	2	3	15	34	f	t	3	quick_attack	sand_attack	\N	\N	\N	2025-09-07 06:12:52.730419
92	408190648924110858	35	20	0	13	6	11	9	4	63	f	f	\N	growl	pound	sing	doubleslap	\N	2025-09-05 13:29:34.020643
84	408190648924110858	1	11	0	14	4	12	15	2	33	f	f	\N	tackle	leech_seed	\N	\N	\N	2025-09-05 11:49:27.526789
85	408190648924110858	104	10	0	15	8	9	6	5	33	f	f	\N	bone_club	growl	\N	\N	\N	2025-09-05 11:49:34.313855
86	408190648924110858	100	21	0	5	1	12	3	0	49	f	f	\N	screech	tackle	sonicboom	thundershock	\N	2025-09-05 11:49:39.532008
87	408190648924110858	150	37	0	2	15	6	13	1	126	f	f	\N	confusion	disable	psychic	swift	\N	2025-09-05 12:05:19.501137
64	137795731951058944	59	28	0	5	14	6	3	15	91	f	f	\N	ember	tackle	leer	flamethrower	\N	2025-08-31 12:54:13.782747
103	137795731951058944	66	8	0	12	6	13	3	13	31	f	f	\N	karate_chop	leer	\N	\N	\N	2025-09-06 07:46:15.957906
96	408190648924110858	151	40	0	5	4	4	7	12	134	f	f	\N	transform	mega_punch	metronome	psychic	\N	2025-09-05 14:54:45.475464
69	137795731951058944	139	23	2133	2	1	15	9	4	66	f	f	\N	rock_throw	tackle	harden	rock_slide	\N	2025-08-31 17:25:15.5681
104	408190648924110858	66	8	0	5	12	13	5	9	30	f	f	\N	karate_chop	leer	\N	\N	\N	2025-09-06 08:02:01.357433
113	137795731951058944	37	24	0	0	0	6	2	14	52	f	f	\N	ember	tail_whip	quick_attack	roar	\N	2025-09-06 19:15:37.643868
65	1008209186913529857	59	28	1671	3	15	7	15	10	90	f	t	3	ember	tackle	leer	flamethrower	\N	2025-08-31 13:08:23.407313
67	1008209186913529857	69	10	1192	8	12	3	0	1	0	f	t	4	vine_whip	growth	\N	\N	\N	2025-08-31 13:57:42.011952
72	137795731951058944	74	16	0	11	10	6	4	6	42	f	f	\N	defense_curl	rock_throw	magnitude	\N	\N	2025-08-31 19:45:01.245484
78	408190648924110858	145	37	0	13	15	9	2	13	123	f	f	\N	thundershock	tackle	thunder_wave	thunderbolt	\N	2025-09-01 03:08:16.392987
79	408190648924110858	139	23	0	3	15	4	13	13	66	f	f	\N	rock_throw	tackle	harden	rock_slide	\N	2025-09-01 03:11:02.166416
66	137795731951058944	69	10	0	0	9	2	3	12	30	f	f	\N	vine_whip	growth	\N	\N	\N	2025-08-31 13:50:39.293655
105	408190648924110858	32	6	0	11	7	0	10	8	22	f	f	\N	acid	sludge	\N	\N	\N	2025-09-06 08:06:43.247518
107	137795731951058944	106	25	0	11	12	6	4	2	65	f	f	\N	double_kick	meditate	karate_chop	leer	\N	2025-09-06 09:39:12.465006
88	408190648924110858	92	18	0	6	2	5	11	10	40	f	f	\N	confuse_ray	lick	night_shade	\N	\N	2025-09-05 12:44:32.835171
93	741060754660130899	35	20	0	14	3	12	1	3	63	f	t	1	growl	pound	sing	doubleslap	\N	2025-09-05 13:29:38.939931
74	137795731951058944	110	20	0	4	14	0	6	6	57	f	f	\N	poison_sting	tackle	acid	sludge	\N	2025-08-31 20:22:25.353551
94	408190648924110858	99	62	0	1	7	4	13	13	141	f	f	\N	guillotine	stomp	crabhammer	harden	\N	2025-09-05 14:30:43.434335
108	774175076366024715	106	25	0	11	0	10	13	2	65	f	f	\N	double_kick	meditate	karate_chop	leer	\N	2025-09-06 11:01:57.98473
68	137795731951058944	55	26	0	6	2	7	13	14	80	f	f	\N	water_gun	tackle	bubble	surf	\N	2025-08-31 15:55:10.707201
97	408190648924110858	23	23	0	5	12	14	9	6	51	f	f	\N	leer	wrap	poison_sting	bite	\N	2025-09-05 14:55:08.24599
114	137795731951058944	43	15	0	11	8	15	5	4	41	f	f	\N	absorb	poisonpowder	vine_whip	\N	\N	2025-09-06 19:15:48.213416
80	137795731951058944	33	19	0	14	10	10	15	4	57	f	f	\N	tackle	poison_sting	horn_attack	\N	\N	2025-09-01 07:39:03.561357
98	408190648924110858	144	60	0	12	14	13	5	2	192	f	f	\N	peck	blizzard	agility	mist	\N	2025-09-05 14:55:25.201058
70	137795731951058944	26	20	0	1	1	14	14	15	54	f	f	\N	thundershock	tackle	thunder_wave	thunderbolt	\N	2025-08-31 17:55:35.95025
89	774175076366024715	92	18	2874	5	3	6	9	0	40	f	t	5	confuse_ray	lick	night_shade	\N	\N	2025-09-05 12:55:42.676563
81	408190648924110858	119	20	0	1	4	4	7	13	62	f	f	\N	peck	supersonic	tail_whip	supersonic	\N	2025-09-01 09:55:59.954225
82	408190648924110858	145	100	0	0	7	4	3	2	290	t	f	\N	thundershock	thunder	agility	light_screen	\N	2025-09-01 10:04:22.787553
95	408190648924110858	12	20	8802	10	11	13	1	9	61	f	t	6	string_shot	tackle	confusion	poison_powder	\N	2025-09-05 14:42:19.32535
119	137795731951058944	8	36	615	12	6	7	9	9	97	f	t	5	water_gun	bite	withdraw	bubble	\N	2025-09-07 07:29:23.622603
76	774175076366024715	74	18	4227	7	2	0	8	4	44	f	t	3	tackle	defense_curl	rock_throw	\N	\N	2025-08-31 23:43:41.439913
106	408190648924110858	29	10	0	1	0	8	1	1	31	f	f	\N	acid	sludge	\N	\N	\N	2025-09-06 08:22:16.970764
91	408190648924110858	123	33	8823	12	8	14	10	2	97	f	t	1	leer	focus_energy	double_team	slash	\N	2025-09-05 13:27:53.23256
109	774175076366024715	133	32	0	3	4	8	3	3	79	f	f	\N	sand_attack	tackle	quick_attack	tail_whip	\N	2025-09-06 11:06:42.594162
101	137795731951058944	52	10	0	15	8	14	12	14	31	f	f	\N	growl	scratch	\N	\N	\N	2025-09-05 17:30:09.61993
112	408190648924110858	37	24	0	12	5	13	6	14	58	f	f	\N	ember	tail_whip	quick_attack	roar	\N	2025-09-06 18:54:04.999673
102	408190648924110858	52	10	0	1	5	5	7	3	28	f	f	\N	growl	scratch	\N	\N	\N	2025-09-05 18:16:25.251147
118	137795731951058944	98	15	0	6	2	8	4	14	35	f	f	\N	bubble	leer	water_gun	\N	\N	2025-09-07 07:10:49.318615
115	446408785804656640	7	5	0	8	7	5	1	15	20	f	t	1	tackle	tail_whip	\N	\N	\N	2025-09-07 04:21:51.66125
116	446408785804656640	7	19	0	9	12	5	5	6	49	f	t	2	tail_whip	water_gun	bubble	\N	\N	2025-09-07 04:22:01.880484
111	137795731951058944	32	7	0	4	14	0	8	10	24	f	f	\N	acid	sludge	\N	\N	\N	2025-09-06 16:22:11.561776
63	137795731951058944	13	14	1954	13	12	6	0	1	38	f	f	\N	string_shot	harden	\N	\N	\N	2025-08-31 12:33:08.781135
62	137795731951058944	130	24	6369	7	14	0	11	2	82	f	t	3	surf	tackle	water_gun	bubble	\N	2025-08-31 12:28:08.248092
77	774175076366024715	144	40	3807	14	7	8	1	13	133	f	t	4	tackle	leer	ice_beam	blizzard	\N	2025-09-01 00:49:05.361194
122	137795731951058944	77	23	0	11	10	3	2	0	61	f	f	\N	ember	tackle	leer	flamethrower	\N	2025-09-07 09:33:13.595374
123	137795731951058944	27	22	0	10	7	15	7	3	58	f	f	\N	scratch	sand_attack	slash	dig	\N	2025-09-07 12:42:32.125767
124	774175076366024715	88	26	0	2	1	15	5	12	78	f	f	\N	disable	pound	poison_sting	tackle	\N	2025-09-07 13:28:06.494287
125	137795731951058944	19	18	0	2	8	2	1	15	39	f	f	\N	tail_whip	hyper_fang	quick_attack	\N	\N	2025-09-07 15:28:16.680363
126	137795731951058944	140	17	0	4	8	12	5	6	38	f	f	\N	harden	scratch	rock_throw	\N	\N	2025-09-07 15:42:37.796566
127	137795731951058944	118	17	0	1	7	8	13	1	42	f	f	\N	peck	tail_whip	water_gun	\N	\N	2025-09-07 16:05:04.0861
128	137795731951058944	63	26	0	3	14	7	3	12	50	f	f	\N	teleport	confusion	psybeam	psychic	\N	2025-09-07 17:49:42.55839
99	774175076366024715	39	14	2532	6	13	1	9	8	57	f	t	6	sing	pound	disable	\N	\N	2025-09-05 15:10:36.935402
100	137795731951058944	1	15	2282	7	15	8	0	11	40	f	t	4	tackle	leech_seed	vine_whip	\N	\N	2025-09-05 15:30:16.550942
121	137795731951058944	50	25	615	8	9	7	13	13	44	f	t	6	scratch	growl	dig	sand_attack	\N	2025-09-07 07:32:02.676833
\.


--
-- Data for Name: pokemon_species; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.pokemon_species (id, name, type1, type2, base_hp, base_attack, base_defense, base_special, base_speed, exp_group, rarity) FROM stdin;
1	Bulbasaur	Grass	Poison	45	49	49	65	45	medium_slow	common
2	Ivysaur	Grass	Poison	60	62	63	80	60	medium_slow	uncommon
3	Venusaur	Grass	Poison	80	82	83	100	80	medium_slow	rare
4	Charmander	Fire	\N	39	52	43	60	65	medium_slow	common
5	Charmeleon	Fire	\N	58	64	58	80	80	medium_slow	uncommon
6	Charizard	Fire	Flying	78	84	78	109	100	medium_slow	rare
7	Squirtle	Water	\N	44	48	65	50	43	medium_slow	common
8	Wartortle	Water	\N	59	63	80	65	58	medium_slow	uncommon
9	Blastoise	Water	\N	79	83	100	85	78	medium_slow	rare
25	Pikachu	Electric	\N	35	55	40	50	90	medium_fast	uncommon
150	Mewtwo	Psychic	\N	106	110	90	154	130	slow	legendary
151	Mew	Psychic	\N	100	100	100	100	100	medium_slow	legendary
10	Caterpie	Bug	\N	45	30	35	20	45	medium_fast	common
11	Metapod	Bug	\N	50	20	55	25	30	medium_fast	uncommon
12	Butterfree	Bug	Flying	60	45	50	90	70	medium_fast	uncommon
13	Weedle	Bug	Poison	40	35	30	20	50	medium_fast	common
14	Kakuna	Bug	Poison	45	25	50	25	35	medium_fast	uncommon
15	Beedrill	Bug	Poison	65	90	40	45	75	medium_fast	uncommon
16	Pidgey	Normal	Flying	40	45	40	35	56	medium_slow	common
17	Pidgeotto	Normal	Flying	63	60	55	50	71	medium_slow	uncommon
18	Pidgeot	Normal	Flying	83	80	75	70	101	medium_slow	rare
19	Rattata	Normal	\N	30	56	35	25	72	medium_fast	common
20	Raticate	Normal	\N	55	81	60	50	97	medium_fast	uncommon
21	Spearow	Normal	Flying	40	60	30	31	70	medium_fast	common
22	Fearow	Normal	Flying	65	90	65	61	100	medium_fast	uncommon
23	Ekans	Poison	\N	35	60	44	40	55	medium_fast	common
24	Arbok	Poison	\N	60	85	69	65	80	medium_fast	uncommon
26	Raichu	Electric	\N	60	90	55	90	110	medium_fast	uncommon
27	Sandshrew	Ground	\N	50	75	85	20	40	medium_fast	common
28	Sandslash	Ground	\N	75	100	110	45	65	medium_fast	uncommon
29	Nidoranâ™€	Poison	\N	55	47	52	40	41	medium_slow	common
30	Nidorina	Poison	\N	70	62	67	55	56	medium_slow	uncommon
31	Nidoqueen	Poison	Ground	90	92	87	75	76	medium_slow	rare
32	Nidoranâ™‚	Poison	\N	46	57	40	40	50	medium_slow	common
33	Nidorino	Poison	\N	61	72	57	55	65	medium_slow	uncommon
34	Nidoking	Poison	Ground	81	102	77	85	85	medium_slow	rare
35	Clefairy	Fairy	\N	70	45	48	60	35	fast	uncommon
36	Clefable	Fairy	\N	95	70	73	95	60	fast	rare
37	Vulpix	Fire	\N	38	41	40	50	65	medium_fast	uncommon
38	Ninetales	Fire	\N	73	76	75	81	100	medium_fast	rare
39	Jigglypuff	Normal	Fairy	115	45	20	45	20	fast	uncommon
40	Wigglytuff	Normal	Fairy	140	70	45	85	45	fast	rare
41	Zubat	Poison	Flying	40	45	35	30	55	medium_fast	common
42	Golbat	Poison	Flying	75	80	70	65	90	medium_fast	uncommon
43	Oddish	Grass	Poison	45	50	55	75	30	medium_slow	common
44	Gloom	Grass	Poison	60	65	70	85	40	medium_slow	uncommon
45	Vileplume	Grass	Poison	75	80	85	110	50	medium_slow	rare
46	Paras	Bug	Grass	35	70	55	45	25	medium_fast	common
47	Parasect	Bug	Grass	60	95	80	60	30	medium_fast	uncommon
48	Venonat	Bug	Poison	60	55	50	40	45	medium_fast	common
49	Venomoth	Bug	Poison	70	65	60	90	90	medium_fast	uncommon
50	Diglett	Ground	\N	10	55	25	35	95	medium_fast	common
51	Dugtrio	Ground	\N	35	80	50	50	120	medium_fast	uncommon
52	Meowth	Normal	\N	40	45	35	40	90	medium_fast	common
53	Persian	Normal	\N	65	70	60	65	115	medium_fast	uncommon
54	Psyduck	Water	\N	50	52	48	65	55	medium_fast	common
55	Golduck	Water	\N	80	82	78	95	85	medium_fast	uncommon
56	Mankey	Fighting	\N	40	80	35	35	70	medium_fast	common
57	Primeape	Fighting	\N	65	105	60	60	95	medium_fast	uncommon
58	Growlithe	Fire	\N	55	70	45	70	60	slow	uncommon
59	Arcanine	Fire	\N	90	110	80	100	95	slow	rare
60	Poliwag	Water	\N	40	50	40	40	90	medium_slow	common
61	Poliwhirl	Water	\N	65	65	65	50	90	medium_slow	uncommon
62	Poliwrath	Water	Fighting	90	95	95	70	70	medium_slow	rare
63	Abra	Psychic	\N	25	20	15	105	90	medium_slow	uncommon
64	Kadabra	Psychic	\N	40	35	30	120	105	medium_slow	rare
65	Alakazam	Psychic	\N	55	50	45	135	120	medium_slow	rare
66	Machop	Fighting	\N	70	80	50	35	35	medium_slow	common
67	Machoke	Fighting	\N	80	100	70	50	45	medium_slow	uncommon
68	Machamp	Fighting	\N	90	130	80	65	55	medium_slow	rare
69	Bellsprout	Grass	Poison	50	75	35	70	40	medium_slow	common
70	Weepinbell	Grass	Poison	65	90	50	85	55	medium_slow	uncommon
71	Victreebel	Grass	Poison	80	105	65	100	70	medium_slow	rare
72	Tentacool	Water	Poison	40	40	35	50	70	slow	common
73	Tentacruel	Water	Poison	80	70	65	80	100	slow	uncommon
74	Geodude	Rock	Ground	40	80	100	30	20	medium_slow	common
75	Graveler	Rock	Ground	55	95	115	45	35	medium_slow	uncommon
76	Golem	Rock	Ground	80	120	130	55	45	medium_slow	rare
77	Ponyta	Fire	\N	50	85	55	65	90	medium_fast	uncommon
78	Rapidash	Fire	\N	65	100	70	80	105	medium_fast	rare
79	Slowpoke	Water	Psychic	90	65	65	40	15	medium_fast	common
80	Slowbro	Water	Psychic	95	75	110	100	30	medium_fast	uncommon
81	Magnemite	Electric	Steel	25	35	70	95	45	medium_fast	uncommon
82	Magneton	Electric	Steel	50	60	95	120	70	medium_fast	rare
83	Farfetch'd	Normal	Flying	52	65	55	58	60	medium_fast	rare
84	Doduo	Normal	Flying	35	85	45	35	75	medium_fast	common
85	Dodrio	Normal	Flying	60	110	70	60	100	medium_fast	uncommon
86	Seel	Water	\N	65	45	55	45	45	medium_fast	uncommon
87	Dewgong	Water	Ice	90	70	80	70	70	medium_fast	rare
88	Grimer	Poison	\N	80	80	50	40	25	medium_fast	uncommon
89	Muk	Poison	\N	105	105	75	65	50	medium_fast	rare
90	Shellder	Water	\N	30	65	100	45	40	slow	uncommon
91	Cloyster	Water	Ice	50	95	180	85	70	slow	rare
92	Gastly	Ghost	Poison	30	35	30	100	80	medium_slow	uncommon
93	Haunter	Ghost	Poison	45	50	45	115	95	medium_slow	rare
94	Gengar	Ghost	Poison	60	65	60	130	110	medium_slow	rare
95	Onix	Rock	Ground	35	45	160	30	70	medium_fast	uncommon
96	Drowzee	Psychic	\N	60	48	45	43	42	medium_fast	common
97	Hypno	Psychic	\N	85	73	70	73	67	medium_fast	uncommon
98	Krabby	Water	\N	30	105	90	25	50	medium_fast	common
99	Kingler	Water	\N	55	130	115	50	75	medium_fast	uncommon
100	Voltorb	Electric	\N	40	30	50	55	100	medium_fast	uncommon
101	Electrode	Electric	\N	60	50	70	80	140	medium_fast	rare
102	Exeggcute	Grass	Psychic	60	40	80	60	40	slow	uncommon
103	Exeggutor	Grass	Psychic	95	95	85	125	55	slow	rare
104	Cubone	Ground	\N	50	50	95	40	35	medium_fast	uncommon
105	Marowak	Ground	\N	60	80	110	50	45	medium_fast	rare
106	Hitmonlee	Fighting	\N	50	120	53	35	87	medium_fast	rare
107	Hitmonchan	Fighting	\N	50	105	79	35	76	medium_fast	rare
108	Lickitung	Normal	\N	90	55	75	60	30	medium_fast	rare
109	Koffing	Poison	\N	40	65	95	60	35	medium_fast	uncommon
110	Weezing	Poison	\N	65	90	120	85	60	medium_fast	rare
111	Rhyhorn	Ground	Rock	80	85	95	30	25	slow	uncommon
112	Rhydon	Ground	Rock	105	130	120	45	40	slow	rare
113	Chansey	Normal	\N	250	5	5	35	50	fast	rare
114	Tangela	Grass	\N	65	55	115	100	60	medium_fast	rare
115	Kangaskhan	Normal	\N	105	95	80	40	90	medium_fast	rare
116	Horsea	Water	\N	30	40	70	70	60	medium_fast	uncommon
117	Seadra	Water	\N	55	65	95	95	85	medium_fast	rare
118	Goldeen	Water	\N	45	67	60	35	63	medium_fast	common
119	Seaking	Water	\N	80	92	65	65	68	medium_fast	uncommon
120	Staryu	Water	\N	30	45	55	70	85	slow	uncommon
121	Starmie	Water	Psychic	60	75	85	100	115	slow	rare
122	Mr. Mime	Psychic	Fairy	40	45	65	100	90	medium_fast	rare
123	Scyther	Bug	Flying	70	110	80	55	105	medium_fast	rare
124	Jynx	Ice	Psychic	65	50	35	115	95	medium_fast	rare
125	Electabuzz	Electric	\N	65	83	57	95	105	medium_fast	rare
126	Magmar	Fire	\N	65	95	57	100	93	medium_fast	rare
127	Pinsir	Bug	\N	65	125	100	55	85	slow	rare
128	Tauros	Normal	\N	75	100	95	40	110	slow	rare
129	Magikarp	Water	\N	20	10	55	15	80	slow	common
130	Gyarados	Water	Flying	95	125	79	60	81	slow	rare
131	Lapras	Water	Ice	130	85	80	85	60	slow	rare
132	Ditto	Normal	\N	48	48	48	48	48	medium_fast	rare
133	Eevee	Normal	\N	55	55	50	45	55	medium_fast	rare
134	Vaporeon	Water	\N	130	65	60	110	65	medium_fast	rare
135	Jolteon	Electric	\N	65	65	60	110	130	medium_fast	rare
136	Flareon	Fire	\N	65	130	60	95	65	medium_fast	rare
137	Porygon	Normal	\N	65	60	70	85	40	medium_fast	rare
138	Omanyte	Rock	Water	35	40	100	90	35	medium_fast	rare
139	Omastar	Rock	Water	70	60	125	115	55	medium_fast	rare
140	Kabuto	Rock	Water	30	80	90	55	55	medium_fast	rare
141	Kabutops	Rock	Water	60	115	105	65	80	medium_fast	rare
142	Aerodactyl	Rock	Flying	80	105	65	60	130	slow	rare
143	Snorlax	Normal	\N	160	110	65	65	30	slow	rare
144	Articuno	Ice	Flying	90	85	100	95	85	slow	legendary
145	Zapdos	Electric	Flying	90	90	85	125	100	slow	legendary
146	Moltres	Fire	Flying	90	100	90	125	90	slow	legendary
147	Dratini	Dragon	\N	41	64	45	50	50	slow	rare
148	Dragonair	Dragon	\N	61	84	65	70	70	slow	rare
149	Dragonite	Dragon	Flying	91	134	95	100	80	slow	rare
\.


--
-- Data for Name: server_config; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.server_config (guild_id, spawn_channels, message_count, messages_until_spawn) FROM stdin;
1410749568899092624	{1411566371480801292}	1	11
696311992973131796	{1413128673061502986,1326949216953831504,1327080626641178764}	1	13
947576847527469137	{947576847527469141}	8	11
1410715548769058838	{1410715549486546976,-1,1410715549486546976}	9	12
1411770019360014468	{1411770019968192584,1411770087513526473,-1,1411770019968192584,1411770087513526473}	8	12
\.


--
-- Data for Name: trades; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.trades (id, requester_id, target_id, pokemon_offered, pokemon_requested, status, created_at, expires_at) FROM stdin;
\.


--
-- Data for Name: user_inventory; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.user_inventory (user_id, item_name, quantity) FROM stdin;
137795731951058944	hm03	1
741060754660130899	hyper_potion	995
137795731951058944	potion	2
774175076366024715	greatball	15
774175076366024715	ultraball	8
408190648924110858	hm03	1
408190648924110858	tm02	2
137795731951058944	super_potion	1
137795731951058944	tm29	0
741060754660130899	greatball	15
741060754660130899	ultraball	8
741060754660130899	masterball	0
137795731951058944	hyper_potion	98
741060754660130899	pokeball	28
408190648924110858	hm04	1
1008209186913529857	pokeball	28
408190648924110858	tm42	0
369809123925295104	pokeball	30
369809123925295104	ultraball	8
272439835694727170	pokeball	0
369809123925295104	masterball	1
272439835694727170	masterball	8
137795731951058944	ultraball	8
137795731951058944	masterball	1
1008209186913529857	masterball	1
408190648924110858	masterball	982
1008209186913529857	greatball	14
369809123925295104	greatball	13
1145424000953090130	greatball	15
1145424000953090130	ultraball	8
1145424000953090130	masterball	1
1145424000953090130	pokeball	28
774175076366024715	masterball	0
1008209186913529857	hyper_potion	20
408190648924110858	pokeball	946
446408785804656640	greatball	15
446408785804656640	ultraball	8
446408785804656640	masterball	1
408190648924110858	rare_candy	98
446408785804656640	pokeball	28
137795731951058944	rare_candy	0
1008209186913529857	ultraball	5
774175076366024715	pokeball	22
408190648924110858	hyper_potion	967
137795731951058944	greatball	11
137795731951058944	pokeball	18
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.users (user_id, username, money, badges, default_pokeball, created_at) FROM stdin;
1008209186913529857	H2Ogoblet	17905	1	pokeball	2025-08-31 04:29:42.555641
774175076366024715	sourpotato	15749	0	pokeball	2025-08-31 11:17:25.272756
137795731951058944	hazelseen	942	7	pokeball	2025-08-31 04:29:42.138705
1145424000953090130	₊ ayama ༯	15033	0	pokeball	2025-08-31 09:10:57.634518
272439835694727170	StockedSix	9601619	0	pokeball	2025-08-29 04:11:03.143495
369809123925295104	Ukra ☀	19451	0	pokeball	2025-08-31 04:25:32.824598
446408785804656640	U know who I am	15000	0	pokeball	2025-09-07 04:21:46.040059
408190648924110858	DBZ Clasher	656755	16	pokeball	2025-08-28 15:23:14.598917
741060754660130899	LavenderBlack	24905	2	pokeball	2025-08-30 15:05:35.864559
\.


--
-- Name: battles_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.battles_id_seq', 37, true);


--
-- Name: pokemon_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.pokemon_id_seq', 128, true);


--
-- Name: trades_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.trades_id_seq', 1, false);


--
-- Name: battles battles_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.battles
    ADD CONSTRAINT battles_pkey PRIMARY KEY (id);


--
-- Name: npc_completions npc_completions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.npc_completions
    ADD CONSTRAINT npc_completions_pkey PRIMARY KEY (user_id, npc_type, npc_index);


--
-- Name: pokemon pokemon_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.pokemon
    ADD CONSTRAINT pokemon_pkey PRIMARY KEY (id);


--
-- Name: pokemon_species pokemon_species_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.pokemon_species
    ADD CONSTRAINT pokemon_species_pkey PRIMARY KEY (id);


--
-- Name: server_config server_config_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.server_config
    ADD CONSTRAINT server_config_pkey PRIMARY KEY (guild_id);


--
-- Name: trades trades_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.trades
    ADD CONSTRAINT trades_pkey PRIMARY KEY (id);


--
-- Name: user_inventory user_inventory_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_inventory
    ADD CONSTRAINT user_inventory_pkey PRIMARY KEY (user_id, item_name);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (user_id);


--
-- Name: idx_battles_active; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_battles_active ON public.battles USING btree (status);


--
-- Name: idx_pokemon_owner; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_pokemon_owner ON public.pokemon USING btree (owner_id);


--
-- Name: idx_pokemon_party; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_pokemon_party ON public.pokemon USING btree (owner_id, in_party);


--
-- Name: idx_trades_active; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_trades_active ON public.trades USING btree (status, expires_at);


--
-- Name: battles battles_challenger_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.battles
    ADD CONSTRAINT battles_challenger_id_fkey FOREIGN KEY (challenger_id) REFERENCES public.users(user_id);


--
-- Name: battles battles_challenger_pokemon_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.battles
    ADD CONSTRAINT battles_challenger_pokemon_fkey FOREIGN KEY (challenger_pokemon) REFERENCES public.pokemon(id);


--
-- Name: battles battles_opponent_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.battles
    ADD CONSTRAINT battles_opponent_id_fkey FOREIGN KEY (opponent_id) REFERENCES public.users(user_id);


--
-- Name: battles battles_opponent_pokemon_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.battles
    ADD CONSTRAINT battles_opponent_pokemon_fkey FOREIGN KEY (opponent_pokemon) REFERENCES public.pokemon(id);


--
-- Name: npc_completions npc_completions_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.npc_completions
    ADD CONSTRAINT npc_completions_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(user_id);


--
-- Name: pokemon pokemon_owner_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.pokemon
    ADD CONSTRAINT pokemon_owner_id_fkey FOREIGN KEY (owner_id) REFERENCES public.users(user_id);


--
-- Name: pokemon pokemon_species_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.pokemon
    ADD CONSTRAINT pokemon_species_id_fkey FOREIGN KEY (species_id) REFERENCES public.pokemon_species(id);


--
-- Name: trades trades_pokemon_offered_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.trades
    ADD CONSTRAINT trades_pokemon_offered_fkey FOREIGN KEY (pokemon_offered) REFERENCES public.pokemon(id);


--
-- Name: trades trades_pokemon_requested_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.trades
    ADD CONSTRAINT trades_pokemon_requested_fkey FOREIGN KEY (pokemon_requested) REFERENCES public.pokemon(id);


--
-- Name: trades trades_requester_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.trades
    ADD CONSTRAINT trades_requester_id_fkey FOREIGN KEY (requester_id) REFERENCES public.users(user_id);


--
-- Name: trades trades_target_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.trades
    ADD CONSTRAINT trades_target_id_fkey FOREIGN KEY (target_id) REFERENCES public.users(user_id);


--
-- Name: user_inventory user_inventory_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_inventory
    ADD CONSTRAINT user_inventory_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(user_id);


--
-- PostgreSQL database dump complete
--

\unrestrict HlUdAdIlvNJ0o6DqMZZHTcixQ6uSA3jRzOPSEkv7shSnt4iDH29kvMpYjcfA5sJ

