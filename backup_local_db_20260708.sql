--
-- PostgreSQL database dump
--

\restrict rheOm5cfkb8eOtxYJGDhPp24omtJikJp30atoio2FJVJTuYzgCTg8AnPhsxlFuw

-- Dumped from database version 16.14
-- Dumped by pg_dump version 16.14

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
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
-- Name: alembic_version; Type: TABLE; Schema: public; Owner: ocean_app
--

CREATE TABLE public.alembic_version (
    version_num character varying(32) NOT NULL
);


ALTER TABLE public.alembic_version OWNER TO ocean_app;

--
-- Name: amenities; Type: TABLE; Schema: public; Owner: ocean_app
--

CREATE TABLE public.amenities (
    id integer NOT NULL,
    subdivision_id integer NOT NULL,
    name character varying(255) NOT NULL,
    scope character varying(20) NOT NULL,
    description text
);


ALTER TABLE public.amenities OWNER TO ocean_app;

--
-- Name: amenities_id_seq; Type: SEQUENCE; Schema: public; Owner: ocean_app
--

CREATE SEQUENCE public.amenities_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.amenities_id_seq OWNER TO ocean_app;

--
-- Name: amenities_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: ocean_app
--

ALTER SEQUENCE public.amenities_id_seq OWNED BY public.amenities.id;


--
-- Name: apartment_specs; Type: TABLE; Schema: public; Owner: ocean_app
--

CREATE TABLE public.apartment_specs (
    id integer NOT NULL,
    subdivision_id integer NOT NULL,
    unit_type character varying(50) NOT NULL,
    area_min numeric(8,2),
    area_max numeric(8,2),
    area_note character varying(100),
    price_min numeric(14,2),
    price_max numeric(14,2),
    price_note character varying(150),
    currency character varying(10) DEFAULT 'VND'::character varying NOT NULL
);


ALTER TABLE public.apartment_specs OWNER TO ocean_app;

--
-- Name: apartment_specs_id_seq; Type: SEQUENCE; Schema: public; Owner: ocean_app
--

CREATE SEQUENCE public.apartment_specs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.apartment_specs_id_seq OWNER TO ocean_app;

--
-- Name: apartment_specs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: ocean_app
--

ALTER SEQUENCE public.apartment_specs_id_seq OWNED BY public.apartment_specs.id;


--
-- Name: conversations; Type: TABLE; Schema: public; Owner: ocean_app
--

CREATE TABLE public.conversations (
    id integer NOT NULL,
    session_id character varying(100) NOT NULL,
    subdivision_id integer,
    status character varying(30) DEFAULT 'active'::character varying NOT NULL,
    started_at timestamp with time zone DEFAULT now() NOT NULL,
    last_message_at timestamp with time zone DEFAULT now() NOT NULL,
    customer_account_id integer
);


ALTER TABLE public.conversations OWNER TO ocean_app;

--
-- Name: conversations_id_seq; Type: SEQUENCE; Schema: public; Owner: ocean_app
--

CREATE SEQUENCE public.conversations_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.conversations_id_seq OWNER TO ocean_app;

--
-- Name: conversations_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: ocean_app
--

ALTER SEQUENCE public.conversations_id_seq OWNED BY public.conversations.id;


--
-- Name: customer_accounts; Type: TABLE; Schema: public; Owner: ocean_app
--

CREATE TABLE public.customer_accounts (
    id integer NOT NULL,
    full_name character varying(255) NOT NULL,
    phone character varying(20) NOT NULL,
    password_hash character varying(500),
    is_active boolean DEFAULT true NOT NULL,
    chat_limit integer DEFAULT 100 NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    email character varying(255),
    budget_min numeric(14,2),
    budget_max numeric(14,2),
    preferred_bedrooms character varying(50),
    customer_type character varying(50) NOT NULL,
    status character varying(30) NOT NULL,
    source character varying(30) NOT NULL,
    summary text,
    assigned_to_id integer
);


ALTER TABLE public.customer_accounts OWNER TO ocean_app;

--
-- Name: customer_accounts_id_seq; Type: SEQUENCE; Schema: public; Owner: ocean_app
--

CREATE SEQUENCE public.customer_accounts_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.customer_accounts_id_seq OWNER TO ocean_app;

--
-- Name: customer_accounts_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: ocean_app
--

ALTER SEQUENCE public.customer_accounts_id_seq OWNED BY public.customer_accounts.id;


--
-- Name: customer_notes; Type: TABLE; Schema: public; Owner: ocean_app
--

CREATE TABLE public.customer_notes (
    id integer NOT NULL,
    customer_account_id integer NOT NULL,
    author_id integer,
    content text NOT NULL,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);


ALTER TABLE public.customer_notes OWNER TO ocean_app;

--
-- Name: customer_notes_id_seq; Type: SEQUENCE; Schema: public; Owner: ocean_app
--

CREATE SEQUENCE public.customer_notes_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.customer_notes_id_seq OWNER TO ocean_app;

--
-- Name: customer_notes_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: ocean_app
--

ALTER SEQUENCE public.customer_notes_id_seq OWNED BY public.customer_notes.id;


--
-- Name: fallback_rules; Type: TABLE; Schema: public; Owner: ocean_app
--

CREATE TABLE public.fallback_rules (
    id integer NOT NULL,
    keyword character varying(255) NOT NULL,
    response_message text NOT NULL,
    priority integer DEFAULT 0 NOT NULL,
    is_active boolean DEFAULT true NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.fallback_rules OWNER TO ocean_app;

--
-- Name: fallback_rules_id_seq; Type: SEQUENCE; Schema: public; Owner: ocean_app
--

CREATE SEQUENCE public.fallback_rules_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.fallback_rules_id_seq OWNER TO ocean_app;

--
-- Name: fallback_rules_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: ocean_app
--

ALTER SEQUENCE public.fallback_rules_id_seq OWNED BY public.fallback_rules.id;


--
-- Name: messages; Type: TABLE; Schema: public; Owner: ocean_app
--

CREATE TABLE public.messages (
    id integer NOT NULL,
    conversation_id integer NOT NULL,
    sender character varying(20) NOT NULL,
    content text NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.messages OWNER TO ocean_app;

--
-- Name: messages_id_seq; Type: SEQUENCE; Schema: public; Owner: ocean_app
--

CREATE SEQUENCE public.messages_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.messages_id_seq OWNER TO ocean_app;

--
-- Name: messages_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: ocean_app
--

ALTER SEQUENCE public.messages_id_seq OWNED BY public.messages.id;


--
-- Name: sales_policies; Type: TABLE; Schema: public; Owner: ocean_app
--

CREATE TABLE public.sales_policies (
    id integer NOT NULL,
    subdivision_id integer NOT NULL,
    title character varying(255) NOT NULL,
    policy_content text NOT NULL,
    status character varying(30) DEFAULT 'published'::character varying NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.sales_policies OWNER TO ocean_app;

--
-- Name: sales_policies_id_seq; Type: SEQUENCE; Schema: public; Owner: ocean_app
--

CREATE SEQUENCE public.sales_policies_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.sales_policies_id_seq OWNER TO ocean_app;

--
-- Name: sales_policies_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: ocean_app
--

ALTER SEQUENCE public.sales_policies_id_seq OWNED BY public.sales_policies.id;


--
-- Name: sales_scopes; Type: TABLE; Schema: public; Owner: ocean_app
--

CREATE TABLE public.sales_scopes (
    id integer NOT NULL,
    user_id integer NOT NULL,
    subdivision_id integer NOT NULL
);


ALTER TABLE public.sales_scopes OWNER TO ocean_app;

--
-- Name: sales_scopes_id_seq; Type: SEQUENCE; Schema: public; Owner: ocean_app
--

CREATE SEQUENCE public.sales_scopes_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.sales_scopes_id_seq OWNER TO ocean_app;

--
-- Name: sales_scopes_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: ocean_app
--

ALTER SEQUENCE public.sales_scopes_id_seq OWNED BY public.sales_scopes.id;


--
-- Name: subdivisions; Type: TABLE; Schema: public; Owner: ocean_app
--

CREATE TABLE public.subdivisions (
    id integer NOT NULL,
    slug character varying(100) NOT NULL,
    name character varying(255) NOT NULL,
    introduction text NOT NULL,
    location text NOT NULL,
    handover_status character varying(255) NOT NULL,
    thumbnail_url character varying(500),
    display_order integer DEFAULT 0 NOT NULL,
    is_published boolean DEFAULT true NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.subdivisions OWNER TO ocean_app;

--
-- Name: subdivisions_id_seq; Type: SEQUENCE; Schema: public; Owner: ocean_app
--

CREATE SEQUENCE public.subdivisions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.subdivisions_id_seq OWNER TO ocean_app;

--
-- Name: subdivisions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: ocean_app
--

ALTER SEQUENCE public.subdivisions_id_seq OWNED BY public.subdivisions.id;


--
-- Name: users; Type: TABLE; Schema: public; Owner: ocean_app
--

CREATE TABLE public.users (
    id integer NOT NULL,
    email character varying(255) NOT NULL,
    full_name character varying(255) NOT NULL,
    password_hash character varying(500) NOT NULL,
    role character varying(20) DEFAULT 'sale'::character varying NOT NULL,
    is_active boolean DEFAULT true NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    avatar_url character varying(500),
    experience_years integer,
    achievements text,
    is_deleted boolean NOT NULL
);


ALTER TABLE public.users OWNER TO ocean_app;

--
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: ocean_app
--

CREATE SEQUENCE public.users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.users_id_seq OWNER TO ocean_app;

--
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: ocean_app
--

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;


--
-- Name: amenities id; Type: DEFAULT; Schema: public; Owner: ocean_app
--

ALTER TABLE ONLY public.amenities ALTER COLUMN id SET DEFAULT nextval('public.amenities_id_seq'::regclass);


--
-- Name: apartment_specs id; Type: DEFAULT; Schema: public; Owner: ocean_app
--

ALTER TABLE ONLY public.apartment_specs ALTER COLUMN id SET DEFAULT nextval('public.apartment_specs_id_seq'::regclass);


--
-- Name: conversations id; Type: DEFAULT; Schema: public; Owner: ocean_app
--

ALTER TABLE ONLY public.conversations ALTER COLUMN id SET DEFAULT nextval('public.conversations_id_seq'::regclass);


--
-- Name: customer_accounts id; Type: DEFAULT; Schema: public; Owner: ocean_app
--

ALTER TABLE ONLY public.customer_accounts ALTER COLUMN id SET DEFAULT nextval('public.customer_accounts_id_seq'::regclass);


--
-- Name: customer_notes id; Type: DEFAULT; Schema: public; Owner: ocean_app
--

ALTER TABLE ONLY public.customer_notes ALTER COLUMN id SET DEFAULT nextval('public.customer_notes_id_seq'::regclass);


--
-- Name: fallback_rules id; Type: DEFAULT; Schema: public; Owner: ocean_app
--

ALTER TABLE ONLY public.fallback_rules ALTER COLUMN id SET DEFAULT nextval('public.fallback_rules_id_seq'::regclass);


--
-- Name: messages id; Type: DEFAULT; Schema: public; Owner: ocean_app
--

ALTER TABLE ONLY public.messages ALTER COLUMN id SET DEFAULT nextval('public.messages_id_seq'::regclass);


--
-- Name: sales_policies id; Type: DEFAULT; Schema: public; Owner: ocean_app
--

ALTER TABLE ONLY public.sales_policies ALTER COLUMN id SET DEFAULT nextval('public.sales_policies_id_seq'::regclass);


--
-- Name: sales_scopes id; Type: DEFAULT; Schema: public; Owner: ocean_app
--

ALTER TABLE ONLY public.sales_scopes ALTER COLUMN id SET DEFAULT nextval('public.sales_scopes_id_seq'::regclass);


--
-- Name: subdivisions id; Type: DEFAULT; Schema: public; Owner: ocean_app
--

ALTER TABLE ONLY public.subdivisions ALTER COLUMN id SET DEFAULT nextval('public.subdivisions_id_seq'::regclass);


--
-- Name: users id; Type: DEFAULT; Schema: public; Owner: ocean_app
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- Data for Name: alembic_version; Type: TABLE DATA; Schema: public; Owner: ocean_app
--

COPY public.alembic_version (version_num) FROM stdin;
529032eb265a
\.


--
-- Data for Name: amenities; Type: TABLE DATA; Schema: public; Owner: ocean_app
--

COPY public.amenities (id, subdivision_id, name, scope, description) FROM stdin;
331	6	Vinbus	external	Vinbus
220	1	Bể bơi ngoài trời	internal	Bể bơi ngoài trời
221	1	Bể bơi trong nhà tiêu chuẩn quốc tế	internal	Bể bơi trong nhà tiêu chuẩn quốc tế
222	1	Chòi nghỉ	internal	Chòi nghỉ
223	1	Cổng torri	internal	Cổng torri
224	1	Ghế nghỉ	internal	Ghế nghỉ
225	1	Hướng nhìn sang tòa S2.18. Phía Tây Bắc : là công viên nội khu với sân chơi trẻ em	internal	Hướng nhìn sang tòa S2.18. Phía Tây Bắc : là công viên nội khu với sân chơi trẻ em
226	1	Hồ cá koi	internal	Hồ cá koi
227	1	Phòng tập Gym	internal	Phòng tập Gym
228	1	Spa	internal	Spa
229	1	Sân thể thao	internal	Sân thể thao
230	1	Sảnh thang máy sang trọng. Phân khu Masteri Waterfront bao gồm 2 tiểu khu là Miami với 3 tòa M1	internal	Sảnh thang máy sang trọng. Phân khu Masteri Waterfront bao gồm 2 tiểu khu là Miami với 3 tòa M1
231	1	Vườn nhiệt đới	internal	Vườn nhiệt đới
232	1	Đường dạo	internal	Đường dạo
233	1	… và các dịch vụ 5 sao với sảnh Lounge	internal	… và các dịch vụ 5 sao với sảnh Lounge
234	1	Biển hồ	external	Biển hồ
235	1	Bệnh viện	external	Bệnh viện
236	1	Công viên	external	Công viên
237	1	Khu căn hộ Masteri Waterfront sở hữu vị trí trái tim trung tâm của khu đô thị với tầm View toàn cảnh hồ Ngọc Trai 24	external	Khu căn hộ Masteri Waterfront sở hữu vị trí trái tim trung tâm của khu đô thị với tầm View toàn cảnh hồ Ngọc Trai 24
238	1	Trung tâm thương mại	external	Trung tâm thương mại
239	1	Vincom	external	Vincom
240	1	Vincom mega mall	external	Vincom mega mall
241	1	Vinmec	external	Vinmec
242	1	Vinuni	external	Vinuni
243	1	Đường lý thánh tông	external	Đường lý thánh tông
244	1	Đại học	external	Đại học
245	2	Bể bơi	internal	Bể bơi
246	2	Bể bơi bốn mùa	internal	Bể bơi bốn mùa
332	6	Vincom	external	Vincom
247	2	Chòi & ghế nghỉ	internal	Chòi & ghế nghỉ
248	2	Chòi nghỉ lục giác hay những tiểu cảnh cổng Torri	internal	Chòi nghỉ lục giác hay những tiểu cảnh cổng Torri
249	2	Gym ngoài trời và phòng tập Gym trong nhà	internal	Gym ngoài trời và phòng tập Gym trong nhà
250	2	Không gian Vườn Nhật The Zenpark nổi bật và cuốn hút với Hồ cá Koi	internal	Không gian Vườn Nhật The Zenpark nổi bật và cuốn hút với Hồ cá Koi
251	2	Nhà để xe	internal	Nhà để xe
252	2	Phòng giải trí	internal	Phòng giải trí
253	2	Phòng sinh hoạt cộng đồng	internal	Phòng sinh hoạt cộng đồng
254	2	Quảng trường	internal	Quảng trường
255	2	Smart home	internal	Smart home
256	2	Spa	internal	Spa
257	2	Sân chơi trẻ em	internal	Sân chơi trẻ em
258	2	Sân thể thao	internal	Sân thể thao
259	2	Sảnh lounge	internal	Sảnh lounge
260	2	Thang máy	internal	Thang máy
261	2	Vườn nhật	internal	Vườn nhật
262	2	Vườn nội khu	internal	Vườn nội khu
263	2	Đường dạo	internal	Đường dạo
264	2	Biển nhân tạo	external	Biển nhân tạo
265	2	Cao tốc Hà Nội – Hải Phòng và đường 379 đi Ecopark. Từ Zenpark	external	Cao tốc Hà Nội – Hải Phòng và đường 379 đi Ecopark. Từ Zenpark
266	2	Công viên	external	Công viên
267	2	Hồ Ngọc Trai (24	external	Hồ Ngọc Trai (24
268	2	Metro số 8	external	Metro số 8
269	2	Vinmec	external	Vinmec
270	2	Vinschool	external	Vinschool
271	2	Đường lý thánh tông	external	Đường lý thánh tông
272	3	Ghế nghỉ	internal	Ghế nghỉ
273	3	Nhà để xe	internal	Nhà để xe
274	3	Quảng trường	internal	Quảng trường
275	3	Smart home	internal	Smart home
276	3	Spa	internal	Spa
277	3	Thang máy	internal	Thang máy
278	3	Đảo Yoga	internal	Đảo Yoga
279	3	Cao tốc hà nội	external	Cao tốc hà nội
280	3	Công viên	external	Công viên
281	3	Ga metro	external	Ga metro
282	3	Quốc lộ 5	external	Quốc lộ 5
283	3	Đường lý thánh tông	external	Đường lý thánh tông
284	4	Spa	internal	Spa
285	4	Biển hồ	external	Biển hồ
286	5	Gym	internal	Gym
287	5	Quảng trường Thụy Sỹ hay hồ cảnh quan Geneva	internal	Quảng trường Thụy Sỹ hay hồ cảnh quan Geneva
288	5	Spa	internal	Spa
289	5	Thang máy	internal	Thang máy
290	5	Thiết bị smart home	internal	Thiết bị smart home
291	5	Tháp đồng hồ	internal	Tháp đồng hồ
292	5	Công viên	external	Công viên
293	5	Deway	external	Deway
294	5	Ga metro	external	Ga metro
295	5	Phân khu cũng được bao quanh bởi hệ thống giáo dục chất lượng cao với trường quốc tế Brighton College	external	Phân khu cũng được bao quanh bởi hệ thống giáo dục chất lượng cao với trường quốc tế Brighton College
296	5	Trường liên cấp	external	Trường liên cấp
297	5	Tuyến metro	external	Tuyến metro
298	5	Vinbus	external	Vinbus
299	5	Vinschool	external	Vinschool
300	5	Xe bus điện	external	Xe bus điện
301	5	Đường Lý Thánh Tông 40m và đường cao tốc Hà Nội – Hải Phòng. Trong tương lai	external	Đường Lý Thánh Tông 40m và đường cao tốc Hà Nội – Hải Phòng. Trong tương lai
302	6	Bể bơi	internal	Bể bơi
303	6	Bể bơi santa monica	internal	Bể bơi santa monica
304	6	Chỉ nhiều hơn tòa Be2 và tòa Be3 . Mỗi tầng chỉ có 26 căn hộ với tổng số 8 thang máy	internal	Chỉ nhiều hơn tòa Be2 và tòa Be3 . Mỗi tầng chỉ có 26 căn hộ với tổng số 8 thang máy
305	6	Game room	internal	Game room
306	6	Gym	internal	Gym
307	6	Hệ thống các công viên tiện ích (sân thể thao	internal	Hệ thống các công viên tiện ích (sân thể thao
308	6	Kid corner	internal	Kid corner
309	6	Quảng trường	internal	Quảng trường
310	6	Sauna	internal	Sauna
311	6	Spa	internal	Spa
312	6	Sân chơi sắc màu	internal	Sân chơi sắc màu
313	6	Sân chơi trẻ em	internal	Sân chơi trẻ em
314	6	Thiết bị smart home	internal	Thiết bị smart home
315	6	Vườn đọc sách	internal	Vườn đọc sách
316	6	Đài phun nước	internal	Đài phun nước
317	6	Biển nhân tạo	external	Biển nhân tạo
318	6	Bộ đôi biển hồ đắt giá	external	Bộ đôi biển hồ đắt giá
319	6	Cao tốc hà nội	external	Cao tốc hà nội
320	6	Cư dân có thể dễ dàng di chuyển tới các tiện ích nội khu đô thị như Hồ Ngọc Trai	external	Cư dân có thể dễ dàng di chuyển tới các tiện ích nội khu đô thị như Hồ Ngọc Trai
321	6	Deway	external	Deway
322	6	Ga metro	external	Ga metro
323	6	Hệ thống các công viên tiện ích (sân thể thao	external	Hệ thống các công viên tiện ích (sân thể thao
324	6	Metro số 8	external	Metro số 8
325	6	Quốc lộ 5	external	Quốc lộ 5
326	6	Trung tâm thương mại	external	Trung tâm thương mại
327	6	Trường học	external	Trường học
328	6	Trường liên cấp Vinschool	external	Trường liên cấp Vinschool
329	6	Trường quốc tế Brighton College	external	Trường quốc tế Brighton College
330	6	Tuyến metro	external	Tuyến metro
333	6	Vincom mega mall	external	Vincom mega mall
334	6	Xe bus điện	external	Xe bus điện
335	6	Đường lý thánh tông	external	Đường lý thánh tông
336	7	An ninh tại tầng 1; Phòng tập Gym	internal	An ninh tại tầng 1; Phòng tập Gym
337	7	Bể bơi	internal	Bể bơi
338	7	Bể bơi santa monica	internal	Bể bơi santa monica
339	7	Gym ngoài trời	internal	Gym ngoài trời
340	7	Hệ thống sân thể thao	internal	Hệ thống sân thể thao
341	7	Phòng giải trí	internal	Phòng giải trí
342	7	Quảng trường	internal	Quảng trường
343	7	Spa	internal	Spa
344	7	Sân chơi trẻ em	internal	Sân chơi trẻ em
345	7	Biển nhân tạo	external	Biển nhân tạo
346	7	Cao tốc hà nội	external	Cao tốc hà nội
347	7	Công viên cây xanh. Các tiện ích trong nhà có Sảnh cư dân	external	Công viên cây xanh. Các tiện ích trong nhà có Sảnh cư dân
348	7	Ga metro	external	Ga metro
349	7	Hồ ngọc trai	external	Hồ ngọc trai
350	7	Quốc lộ 5	external	Quốc lộ 5
351	7	Trường liên cấp Vinschool	external	Trường liên cấp Vinschool
352	7	Tuyến metro	external	Tuyến metro
353	7	Vincom Mega Mall	external	Vincom Mega Mall
354	7	Đường lý thánh tông	external	Đường lý thánh tông
355	7	Đại họ Vinuni	external	Đại họ Vinuni
356	8	An ninh	internal	An ninh
357	8	Bể bơi ngoài trời	internal	Bể bơi ngoài trời
358	8	Chòi nghỉ hoàng gia	internal	Chòi nghỉ hoàng gia
359	8	Phòng giải trí	internal	Phòng giải trí
360	8	Phòng sinh hoạt cộng đồng	internal	Phòng sinh hoạt cộng đồng
361	8	Phòng tập Gym	internal	Phòng tập Gym
362	8	Quảng trường	internal	Quảng trường
363	8	Smart home	internal	Smart home
364	8	Spa	internal	Spa
365	8	Sân chơi trẻ em phong cách vườn xích đu cổ tích	internal	Sân chơi trẻ em phong cách vườn xích đu cổ tích
366	8	Sân thể thao	internal	Sân thể thao
367	8	Thang máy	internal	Thang máy
368	8	Tổ hợp bể bơi Infinity Oasis người lớn và trẻ em chủ đề biển cả	internal	Tổ hợp bể bơi Infinity Oasis người lớn và trẻ em chủ đề biển cả
369	8	Yoga	internal	Yoga
370	8	BBQ ngoài trời; Trung tâm thương mại Vincom Mega Mall	external	BBQ ngoài trời; Trung tâm thương mại Vincom Mega Mall
371	8	Cao tốc hà nội	external	Cao tốc hà nội
372	8	Công viên	external	Công viên
373	8	Deway	external	Deway
374	8	Hồ Ngọc Trai 24	external	Hồ Ngọc Trai 24
375	8	Metro số 8	external	Metro số 8
376	8	Phòng khám đa khoa Vinmec	external	Phòng khám đa khoa Vinmec
377	8	Quốc lộ 5	external	Quốc lộ 5
378	8	Trung tâm thương mại	external	Trung tâm thương mại
379	8	Trường học	external	Trường học
380	8	Trường liên cấp	external	Trường liên cấp
381	8	Trường quốc tế Brighton College	external	Trường quốc tế Brighton College
382	8	Tuyến metro	external	Tuyến metro
383	8	Vinbus	external	Vinbus
384	8	Vincom	external	Vincom
385	8	Vinschool	external	Vinschool
386	8	Xe bus điện	external	Xe bus điện
387	8	Đường lý thánh tông	external	Đường lý thánh tông
388	8	Đại học Vinuni	external	Đại học Vinuni
389	9	3PN (thang máy riêng)	internal	3PN (thang máy riêng)
390	9	Spa	internal	Spa
391	9	Biển hồ	external	Biển hồ
392	9	Crystal lagoon	external	Crystal lagoon
393	9	Công viên	external	Công viên
394	9	Hồ Ngọc Trai và Biển nhân tạo.	external	Hồ Ngọc Trai và Biển nhân tạo.
395	9	Hồ ngọc trai	external	Hồ ngọc trai
396	9	Đường lý thánh tông	external	Đường lý thánh tông
397	10	Bể bơi 4 mùa	internal	Bể bơi 4 mùa
398	10	Bể bơi trong nhà	internal	Bể bơi trong nhà
399	10	Gym ngoài trời	internal	Gym ngoài trời
400	10	Hệ thống công viên tiện ích nội khu với bể bơi ngoài trời	internal	Hệ thống công viên tiện ích nội khu với bể bơi ngoài trời
401	10	Phòng tập Gym	internal	Phòng tập Gym
402	10	Spa	internal	Spa
403	10	Sân chơi trẻ em	internal	Sân chơi trẻ em
404	10	Sân thể thao	internal	Sân thể thao
405	10	Sảnh lounge	internal	Sảnh lounge
406	10	5ha và Biển nhân tạo Crystal Largoon 6	external	5ha và Biển nhân tạo Crystal Largoon 6
407	10	Ban công kính cường lực thời thượng. Là một phân khu căn hộ nằm trong tổng thể Thành phố biển hồ Vinhomes Ocean Park	external	Ban công kính cường lực thời thượng. Là một phân khu căn hộ nằm trong tổng thể Thành phố biển hồ Vinhomes Ocean Park
408	10	Bênh viện Vinmec	external	Bênh viện Vinmec
409	10	Deway	external	Deway
410	10	Hệ thống công viên tiện ích nội khu với bể bơi ngoài trời	external	Hệ thống công viên tiện ích nội khu với bể bơi ngoài trời
411	10	Hồ ngọc trai	external	Hồ ngọc trai
412	10	Sân bay nội bài	external	Sân bay nội bài
413	10	Trung tâm thương mại	external	Trung tâm thương mại
414	10	Trường học	external	Trường học
415	10	Trường liên cấp Vinschool	external	Trường liên cấp Vinschool
416	10	Trường quốc tế Brighton College	external	Trường quốc tế Brighton College
417	10	Vincom	external	Vincom
418	10	Vincom mega mall	external	Vincom mega mall
419	10	Đại học Vinuni	external	Đại học Vinuni
420	11	Spa	internal	Spa
421	11	Biển hồ	external	Biển hồ
422	11	Công viên	external	Công viên
423	11	Trường học và khu phố thương mại Biển Hồ 10A. Phía Tây Nam : tiếp giáp đường Biể	external	Trường học và khu phố thương mại Biển Hồ 10A. Phía Tây Nam : tiếp giáp đường Biể
424	11	Tuyến metro	external	Tuyến metro
425	11	Đường lý thánh tông	external	Đường lý thánh tông
426	12	An ninh	internal	An ninh
427	12	Bể bơi ngoài trời dài 50m	internal	Bể bơi ngoài trời dài 50m
428	12	Compound	internal	Compound
429	12	Nhà để xe	internal	Nhà để xe
430	12	Phòng tập Gym & xông hơi	internal	Phòng tập Gym & xông hơi
431	12	Spa	internal	Spa
432	12	Biển hồ	external	Biển hồ
433	12	Cao tốc hà nội	external	Cao tốc hà nội
434	12	Khi tuyến tàu điện Metro số 8 hoàn thành và đưa vào sử dụng	external	Khi tuyến tàu điện Metro số 8 hoàn thành và đưa vào sử dụng
435	12	Quốc lộ 5	external	Quốc lộ 5
436	12	Trường học	external	Trường học
437	12	Tuyến metro	external	Tuyến metro
438	12	Đường lý thánh tông	external	Đường lý thánh tông
\.


--
-- Data for Name: apartment_specs; Type: TABLE DATA; Schema: public; Owner: ocean_app
--

COPY public.apartment_specs (id, subdivision_id, unit_type, area_min, area_max, area_note, price_min, price_max, price_note, currency) FROM stdin;
68	1	Studio	25.00	41.00	25 – 41m²	1800000000.00	2200000000.00	1,8 – 2,2 tỷ	VND
69	1	1PN	35.00	49.00	35 – 49m²	2100000000.00	2800000000.00	2,1 – 2,8 tỷ	VND
70	1	2PN	53.00	75.00	53 – 75m²	3200000000.00	4500000000.00	3,2 – 4,5 tỷ	VND
71	1	3PN	73.00	105.00	73 – 105m²	4500000000.00	6500000000.00	4,5 – 6,5 tỷ	VND
72	1	1PN+1	42.50	43.90	42,5 – 43,9m²	2300000000.00	2700000000.00	2.3 – 2.7 tỷ	VND
73	1	2PN+1	54.60	63.70	54,6 – 63,7m²	3200000000.00	4500000000.00	3.2 – 4.5 tỷ	VND
74	2	Studio	27.00	30.00	27 – 30m²	1200000000.00	1600000000.00	1,2 – 1,6 tỷ	VND
75	2	1PN	41.00	45.00	41 – 45m²	1700000000.00	2300000000.00	1,7 – 2,3 tỷ	VND
76	2	2PN	64.00	70.00	64 – 70m²	3000000000.00	3500000000.00	3,0 – 3,5 tỷ	VND
77	2	3PN	76.00	82.00	76 – 82m²	3500000000.00	4800000000.00	3,5 – 4,8 tỷ	VND
78	2	1PN+1	47.00	52.00	47 – 52m²	2000000000.00	2500000000.00	2,0 – 2,5 tỷ	VND
79	2	2PN+1	74.00	77.00	74 – 77m²	3500000000.00	4300000000.00	3,5 – 4,3 tỷ	VND
80	2	3PN+1	88.00	100.60	88 – 100,6m²	\N	\N	Đã bán hết	VND
81	3	Studio	27.00	35.00	27 – 35m²	1400000000.00	1600000000.00	1,4 – 1,6 tỷ	VND
82	3	1PN	35.00	47.00	35 – 47m²	1600000000.00	2300000000.00	1,6 – 2,3 tỷ	VND
83	3	2PN	53.00	74.00	53 – 74m²	2400000000.00	3300000000.00	2,4 – 3,3 tỷ	VND
84	3	3PN	78.00	99.50	78 – 99,5m²	4100000000.00	5100000000.00	4,1 – 5,1 tỷ	VND
85	3	1PN+1	43.00	48.00	43 – 48m²	2000000000.00	2300000000.00	2,0 – 2,3 tỷ	VND
86	5	Studio	27.00	36.00	27 – 36m²	\N	\N	đã bán hết!	VND
87	5	1PN	41.00	48.00	41 – 48m²	\N	\N	đã bán hết!	VND
88	5	2PN	54.00	75.00	54 – 75m²	\N	\N	đã bán hết!	VND
89	5	3PN	88.00	105.00	88 – 105m²	\N	\N	đã bán hết!	VND
90	6	Studio	28.00	36.00	28 – 36m²	1800000000.00	2100000000.00	1,8 – 2,1 tỷ	VND
91	6	1PN	43.20	48.60	43,2 – 48,6m²	2500000000.00	3200000000.00	2,5 – 3,2 tỷ	VND
92	6	2PN	54.40	75.30	54,4 – 75,3m²	3100000000.00	4200000000.00	3,1 – 4,2 tỷ	VND
93	6	3PN	81.50	109.20	81,5 – 109,2m²	5300000000.00	6500000000.00	5,3 – 6,5 tỷ	VND
94	6	2PN+1	76.20	79.00	76,2 – 79m²	4200000000.00	4500000000.00	4,2 – 4,5 tỷ	VND
95	7	Studio	26.60	38.00	26,6 – 38m²	1700000000.00	2200000000.00	1,7 – 2,2 tỷ	VND
96	7	1PN	37.20	43.90	37,2 – 43,9m²	2300000000.00	2700000000.00	2,3 – 2,7 tỷ	VND
97	7	2PN	56.80	64.20	56,8 – 64,2m²	3700000000.00	4100000000.00	3,7 – 4,1 tỷ	VND
98	7	3PN	81.60	99.50	81,6 – 99,5m²	5000000000.00	6500000000.00	5 – 6,5 tỷ	VND
99	7	1PN+1	47.60	48.40	47,6 – 48,4m²	2800000000.00	3200000000.00	2,8 – 3,2 tỷ	VND
100	7	2PN+1	76.70	76.70	76,7m²	4400000000.00	4700000000.00	4,4 – 4,7 tỷ	VND
101	8	Studio	27.10	30.90	27,1 – 30,9m²	1800000000.00	2200000000.00	1,8 – 2,2 tỷ	VND
102	8	1PN	42.70	43.50	42,7 – 43,5m²	2700000000.00	2800000000.00	2,7 – 2,8 tỷ	VND
103	8	2PN	61.10	74.20	61,1 – 74,2m²	3800000000.00	4200000000.00	3,8 – 4,2 tỷ	VND
104	8	3PN	83.80	97.40	83,8 – 97,4m²	5100000000.00	6200000000.00	5,1 – 6,2 tỷ	VND
105	8	4 ngủ	113.10	113.10	113,1m²	6700000000.00	7300000000.00	6,7 – 7,3 tỷ	VND
106	8	1PN+1	46.50	54.80	46,5 – 54,8m²	2900000000.00	3300000000.00	2,9 – 3,3 tỷ	VND
107	8	2PN+1	73.70	76.80	73,7 – 76,8m²	4600000000.00	4900000000.00	4,6 – 4,9 tỷ	VND
108	9	Studio	28.60	31.60	28,6 – 31,6m²	3000000000.00	3900000000.00	3 – 3,9 tỷ	VND
109	9	1PN	39.30	41.30	39,3 – 41,3m²	4000000000.00	4900000000.00	4 – 4,9 tỷ	VND
110	9	1PN+1	46.10	47.20	46,1 – 47,2m²	4300000000.00	5800000000.00	4,3 – 5,8 tỷ	VND
111	9	2PN	58.80	63.30	58,8 – 63,3m²	5700000000.00	7200000000.00	5,7 – 7,2 tỷ	VND
112	9	2PN+1	63.50	69.20	63,5 – 69,2m²	6500000000.00	7900000000.00	6,5 – 7,9 tỷ	VND
113	9	3PN	78.50	89.20	78,5 – 89,2m²	8700000000.00	11200000000.00	8,7 – 11,2 tỷ	VND
114	9	3PN (thang máy)	92.50	93.90	92,5 – 93,9m²	10400000000.00	12300000000.00	10,4 – 12,3 tỷ	VND
115	9	Duplex	171.00	186.10	171 – 186,1m²	\N	\N	liên hệ	VND
116	9	Penthouse	\N	\N	Đang cập nhật	\N	\N	Liên hệ	VND
117	10	Studio	25.00	35.00	25 – 35m²	1300000000.00	2300000000.00	1,3 – 2,3 tỷ	VND
118	10	1PN	1.00	42.00	1 42 – 48m²	2200000000.00	3300000000.00	2,2 – 3,3 tỷ	VND
119	10	2PN	54.00	63.00	54 – 63m²	3200000000.00	4200000000.00	3,2 – 4,2 tỷ	VND
120	10	3PN	74.00	80.00	74 – 80m²	4500000000.00	7200000000.00	4,5 – 7,2 tỷ	VND
121	10	1PN+1	42.00	48.00	42 – 48m²	2200000000.00	3300000000.00	2,2 – 3,3 tỷ	VND
122	10	2PN+1	63.00	64.00	63 – 64m²	3600000000.00	4900000000.00	3,6 – 4,9 tỷ	VND
123	11	Studio	25.60	26.50	25,6 – 26,5m²	2000000000.00	2300000000.00	2 – 2,3 tỷ	VND
124	11	1PN+1	45.50	47.00	45,5 – 47m²	3000000000.00	3800000000.00	3,0 – 3,8 tỷ	VND
125	11	2PN	61.50	64.00	61,5 – 64m²	4200000000.00	5300000000.00	4,2 – 5,3 tỷ	VND
126	11	2PN+1	63.80	66.80	63,8 – 66,8m²	4600000000.00	5500000000.00	4,6 – 5,5 tỷ	VND
127	11	3PN	82.00	82.40	82 – 82,4m²	6200000000.00	7100000000.00	6,2 – 7,1 tỷ	VND
128	11	Penthouse	\N	\N	Đang cập nhật	\N	\N	Đang cập nhật	VND
129	12	1PN	42.00	42.00	42m²	2000000000.00	19000000000.00	Tầng 2 – 19 đang cập nhật!	VND
130	12	2PN	54.00	81.00	54 – 81m²	2000000000.00	36000000000.00	Tầng 2 – 36 đang cập nhật!	VND
131	12	3PN	83.00	108.00	83 – 108m²	2000000000.00	37000000000.00	Tầng 2 – 37 đang cập nhật!	VND
132	12	4PN	154.00	188.00	154 – 188m²	37000000000.00	37000000000.00	Tầng 37 đang cập nhật!	VND
133	12	Duplex	118.00	190.00	118 – 190m²	2000000000.00	37000000000.00	Tầng 2 – 37 đang cập nhật!	VND
134	12	Penthouse	352.00	432.00	352 – 432m²	36000000000.00	37000000000.00	Tầng 36 – 37 đang cập nhật!	VND
\.


--
-- Data for Name: conversations; Type: TABLE DATA; Schema: public; Owner: ocean_app
--

COPY public.conversations (id, session_id, subdivision_id, status, started_at, last_message_at, customer_account_id) FROM stdin;
\.


--
-- Data for Name: customer_accounts; Type: TABLE DATA; Schema: public; Owner: ocean_app
--

COPY public.customer_accounts (id, full_name, phone, password_hash, is_active, chat_limit, created_at, updated_at, email, budget_min, budget_max, preferred_bedrooms, customer_type, status, source, summary, assigned_to_id) FROM stdin;
\.


--
-- Data for Name: customer_notes; Type: TABLE DATA; Schema: public; Owner: ocean_app
--

COPY public.customer_notes (id, customer_account_id, author_id, content, created_at) FROM stdin;
\.


--
-- Data for Name: fallback_rules; Type: TABLE DATA; Schema: public; Owner: ocean_app
--

COPY public.fallback_rules (id, keyword, response_message, priority, is_active, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: messages; Type: TABLE DATA; Schema: public; Owner: ocean_app
--

COPY public.messages (id, conversation_id, sender, content, created_at) FROM stdin;
\.


--
-- Data for Name: sales_policies; Type: TABLE DATA; Schema: public; Owner: ocean_app
--

COPY public.sales_policies (id, subdivision_id, title, policy_content, status, created_at, updated_at) FROM stdin;
41	11	Chính sách bán hàng	Các đợt đóng tiền Tỷ lệ thanh toán	published	2026-07-07 16:11:56.312538+00	2026-07-07 16:11:56.312538+00
42	11	Chính sách bán hàng	Đặt cọc : Ký Xác nhận đăng ký (XNĐK) 50.000.000 VNĐ	published	2026-07-07 16:11:56.312538+00	2026-07-07 16:11:56.312538+00
43	11	Chính sách bán hàng	Lần 1 : Ký Văn bản thỏa thuận (VBTT) – Trong vòng 7 ngày kể từ ngày đặt cọc 10% giá trị căn hộ (không gồm VAT) đã bao gồm tiền đặt cọc	published	2026-07-07 16:11:56.312538+00	2026-07-07 16:11:56.312538+00
44	11	Chính sách bán hàng	Lần 2 : Ký Hợp đồng mua bán (HĐMB) – Dự kiến tháng 1/2025 15% giá trị căn hộ (gồm VAT, đã gồm 10% giá trị căn không gồm VAT đã đóng) + 5% giá trị căn hộ (không gồm VAT) vào Thỏa thuận đặt cọc (TTĐC) đảm bảo thực hiện HĐMB	published	2026-07-07 16:11:56.312538+00	2026-07-07 16:11:56.312538+00
45	11	Chính sách bán hàng	Lần 3 : ngày 15/04/2025 10% giá trị căn hộ (gồm VAT)	published	2026-07-07 16:11:56.312538+00	2026-07-07 16:11:56.312538+00
46	11	Chính sách bán hàng	Lần 4 : ngày 15/07/2025 10% giá trị căn hộ (gồm VAT)	published	2026-07-07 16:11:56.312538+00	2026-07-07 16:11:56.312538+00
47	11	Chính sách bán hàng	Lần 5 : ngày 15/10/2025 10% giá trị căn hộ (gồm VAT)	published	2026-07-07 16:11:56.312538+00	2026-07-07 16:11:56.312538+00
48	11	Chính sách bán hàng	Lần 6 : ngày 15/01/2026 10% giá trị căn hộ (gồm VAT)	published	2026-07-07 16:11:56.312538+00	2026-07-07 16:11:56.312538+00
49	11	Chính sách bán hàng	Lần 7 : ngày 15/04/2026 10% giá trị căn hộ (gồm VAT)	published	2026-07-07 16:11:56.312538+00	2026-07-07 16:11:56.312538+00
50	11	Chính sách bán hàng	Lần 8 : ngày 15/07/2026 05% giá trị căn hộ (gồm VAT)	published	2026-07-07 16:11:56.312538+00	2026-07-07 16:11:56.312538+00
51	11	Chính sách bán hàng	Lần 9 : Theo thông báo bàn giao nhà – Dự kiến Quý 4/2026 25% giá trị căn hộ (gồm VAT) + 100% Kinh phí bảo trì (KPBT) + VAT của 5% giá trị căn hộ	published	2026-07-07 16:11:56.312538+00	2026-07-07 16:11:56.312538+00
52	11	Chính sách bán hàng	Lần 2 : Ký Hợp đồng mua bán (HĐMB) – Dự kiến tháng 1/2025 25% giá trị căn hộ (gồm VAT, đã gồm 10% giá trị căn không gồm VAT đã đóng) + 5% giá trị căn hộ (không gồm VAT) vào Thỏa thuận đặt cọc (TTĐC) đảm bảo thực hiện HĐMB	published	2026-07-07 16:11:56.312538+00	2026-07-07 16:11:56.312538+00
53	11	Chính sách bán hàng	Lần 3 : ngày 15/04/2025 70% giá trị căn hộ (gồm VAT)	published	2026-07-07 16:11:56.312538+00	2026-07-07 16:11:56.312538+00
54	11	Chính sách bán hàng	Lần 4 : Theo thông báo bàn giao nhà – Dự kiến Quý 4/2026 100% Kinh phí bảo trì (KPBT) + VAT của 5% giá trị căn hộ	published	2026-07-07 16:11:56.312538+00	2026-07-07 16:11:56.312538+00
55	11	Chính sách bán hàng	Các đợt đóng tiền Vốn tự có Ngân hàng giải ngân	published	2026-07-07 16:11:56.312538+00	2026-07-07 16:11:56.312538+00
56	11	Chính sách bán hàng	Lần 2 : Ký Hợp đồng mua bán (HĐMB) – Dự kiến tháng 1/2025 20% giá trị căn hộ (gồm VAT, đã gồm 10% giá trị căn không gồm VAT đã đóng)	published	2026-07-07 16:11:56.312538+00	2026-07-07 16:11:56.312538+00
57	11	Chính sách bán hàng	Lần 3 : Trong vòng 30 ngày kể từ ngày ký HĐMB 70% giá trị căn hộ (gồm VAT)	published	2026-07-07 16:11:56.312538+00	2026-07-07 16:11:56.312538+00
58	11	Chính sách bán hàng	Lần 4 : Theo thông báo bàn giao nhà – Dự kiến Quý 4/2026 10% giá trị căn hộ (gồm VAT) + 100% Kinh phí bảo trì (KPBT)	published	2026-07-07 16:11:56.312538+00	2026-07-07 16:11:56.312538+00
59	11	Chính sách bán hàng	Lần 3 : Trong vòng 30 ngày kể từ ngày ký HĐMB 5% giá trị căn hộ (gồm VAT) 50% giá trị căn hộ (gồm VAT)	published	2026-07-07 16:11:56.312538+00	2026-07-07 16:11:56.312538+00
60	11	Chính sách bán hàng	Lần 4 : Theo thông báo bàn giao nhà – Dự kiến Quý 4/2026 25% giá trị căn hộ (gồm VAT) + 100% Kinh phí bảo trì (KPBT) + VAT của 5% giá trị căn hộ	published	2026-07-07 16:11:56.312538+00	2026-07-07 16:11:56.312538+00
61	12	Chính sách bán hàng	Các đợt đóng tiền Tỷ lệ thanh toán	published	2026-07-07 16:11:56.312538+00	2026-07-07 16:11:56.312538+00
62	12	Chính sách bán hàng	Lần 1 : Booking (đặt chỗ): Ký Quỹ có hoàn lại 200.000.000 VNĐ	published	2026-07-07 16:11:56.312538+00	2026-07-07 16:11:56.312538+00
63	12	Chính sách bán hàng	Lần 2 : Ký Thỏa thuận ký Quỹ (TTKQ) – Quý 4/2024 5% giá trị căn hộ đã bao gồm tiền đặt chỗ Booking	published	2026-07-07 16:11:56.312538+00	2026-07-07 16:11:56.312538+00
64	12	Chính sách bán hàng	Lần 3 : Ký Hợp đồng mua bán (HĐMB) – Quý 1/2025 15% giá trị căn hộ (gồm VAT)	published	2026-07-07 16:11:56.312538+00	2026-07-07 16:11:56.312538+00
65	12	Chính sách bán hàng	Lần 4 : Quý 2/2025 5% giá trị căn hộ (gồm VAT)	published	2026-07-07 16:11:56.312538+00	2026-07-07 16:11:56.312538+00
66	12	Chính sách bán hàng	Lần 5 : Quý 3/2025 5% giá trị căn hộ (gồm VAT)	published	2026-07-07 16:11:56.312538+00	2026-07-07 16:11:56.312538+00
67	12	Chính sách bán hàng	Lần 6 : Quý 4/2025 5% giá trị căn hộ (gồm VAT)	published	2026-07-07 16:11:56.312538+00	2026-07-07 16:11:56.312538+00
68	12	Chính sách bán hàng	Lần 7 : Quý 1/2026 5% giá trị căn hộ (gồm VAT)	published	2026-07-07 16:11:56.312538+00	2026-07-07 16:11:56.312538+00
69	12	Chính sách bán hàng	Lần 8 : Quý 2/2026 5% giá trị căn hộ (gồm VAT)	published	2026-07-07 16:11:56.312538+00	2026-07-07 16:11:56.312538+00
70	12	Chính sách bán hàng	Lần 9 : Quý 3/2026 5% giá trị căn hộ (gồm VAT)	published	2026-07-07 16:11:56.312538+00	2026-07-07 16:11:56.312538+00
71	12	Chính sách bán hàng	Lần 10 : Theo thông báo bàn giao nhà – Dự kiến Quý 2/2027 45% giá trị căn hộ (gồm VAT) + VAT của 5% giá trị căn hộ + 100% Kinh phí bảo trì (KPBT)	published	2026-07-07 16:11:56.312538+00	2026-07-07 16:11:56.312538+00
72	12	Chính sách bán hàng	Lần 10 : Theo thông báo làm sổ đỏ 5% giá trị căn hộ (không gồm VAT)	published	2026-07-07 16:11:56.312538+00	2026-07-07 16:11:56.312538+00
73	12	Chính sách bán hàng	Lần 4 : Quý 2/2025 30% giá trị căn hộ (gồm VAT)	published	2026-07-07 16:11:56.312538+00	2026-07-07 16:11:56.312538+00
74	12	Chính sách bán hàng	Lần 5 : Theo thông báo bàn giao nhà – Dự kiến Quý 2/2027 45% giá trị căn hộ (gồm VAT) + VAT của 5% giá trị căn hộ + 100% Kinh phí bảo trì (KPBT)	published	2026-07-07 16:11:56.312538+00	2026-07-07 16:11:56.312538+00
75	12	Chính sách bán hàng	Lần 6 : Theo thông báo làm sổ đỏ 5% giá trị căn hộ (không gồm VAT)	published	2026-07-07 16:11:56.312538+00	2026-07-07 16:11:56.312538+00
76	12	Chính sách bán hàng	Các đợt đóng tiền Vốn tự có Ngân hàng giải ngân	published	2026-07-07 16:11:56.312538+00	2026-07-07 16:11:56.312538+00
77	12	Chính sách bán hàng	Lần 4 : Quý 2/2025 10% giá trị căn hộ (gồm VAT)	published	2026-07-07 16:11:56.312538+00	2026-07-07 16:11:56.312538+00
78	12	Chính sách bán hàng	Lần 5 : Quý 4/2025 10% giá trị căn hộ (gồm VAT)	published	2026-07-07 16:11:56.312538+00	2026-07-07 16:11:56.312538+00
79	12	Chính sách bán hàng	Lần 6 : Quý 2/2026 10% giá trị căn hộ (gồm VAT)	published	2026-07-07 16:11:56.312538+00	2026-07-07 16:11:56.312538+00
80	12	Chính sách bán hàng	Lần 7 : Theo thông báo bàn giao nhà – Dự kiến Quý 2/2027 45% giá trị căn hộ (gồm VAT) + VAT của 5% giá trị căn hộ + 100% Kinh phí bảo trì (KPBT)	published	2026-07-07 16:11:56.312538+00	2026-07-07 16:11:56.312538+00
\.


--
-- Data for Name: sales_scopes; Type: TABLE DATA; Schema: public; Owner: ocean_app
--

COPY public.sales_scopes (id, user_id, subdivision_id) FROM stdin;
\.


--
-- Data for Name: subdivisions; Type: TABLE DATA; Schema: public; Owner: ocean_app
--

COPY public.subdivisions (id, slug, name, introduction, location, handover_status, thumbnail_url, display_order, is_published, created_at, updated_at) FROM stdin;
1	the-sapphire	The Sapphire	Chung cư Vinhomes Ocean Park được triển khai thi công từ năm 2018 và bắt đầu bàn giao từ khoảng tháng 4 năm 2020 với các căn hộ phân khu Sapphire 2. Đến thời điểm hiện tại, nơi đây đã hình thành nên một khu đô thị vô cùng hiện đại và tiện nghi với không gian sống sinh thái trong lành và thư thái.\n\nCảnh quan các phân khu căn hộ Vinhomes Ocean Park được thiết kế theo các phong cách kiến trúc tinh hoa hàng đầu thế giới như Singapore, Nhật Bản, Thụy Sỹ, Dubai, … Chỉ trong thời gian khoảng 5 năm kể từ thời điểm khởi công, Ocean Park đã kiến tạo nên một “thành phố sinh thái thu nhỏ” với một cộng đồng cư dân văn minh.\n\nĐặc biệt, với nhiều chính sách hỗ trợ ưu đãi và giá bán chỉ từ 1,3 tỷ/căn , căn hộ Vin Ocean Park thực sự đã trở thành một trong những sự lựa chọn hàng đầu cho mọi khách hàng đang tìm kiếm cho mình và gia đình một khôi nhà mơ ước.\n\nCác căn hộ tại phân khu The Sapphire là phân khúc căn hộ có giá bán thấp nhất tại dự án Vinhomes Ocean Park, chỉ khoảng 30 – 40 triệu/m2 với tiêu chuẩn ban giao nội thất tiêu chuẩn. Căn hộ có diện tích từ khoảng 25 – 98,5m2 với các loại hình căn hộ Studio, 1 ngủ, 1 ngủ + 1, 2 ngủ, 2 ngủ + 1 và 3 ngủ.	The Ocean View Vinhomes Ocean Park là phân khu chung cư được mở bán tiếp theo phân khu The Sapphire. Được quy hoạch theo mô hình “Nghỉ dưỡng sinh thái đẳng cấp” giữa biển xanh khoáng đạt, The Ocean View là nơi mà cư dân có thể thư thái tận hưởng sự tiện nghi của thiên đường tiện ích, sự trong lành của không “ốc đảo xanh” và sự yên tĩnh ngạy tại một Đại đô thị sôi động.\n\nSở hữu vị trí của ngõ của “Quận Ocean”, The Metropolitan nằm tại mặt đường Lý Thánh Tông và chạy dọc theo công viên hồ San Hô lớn bậc nhất tại dự án. The Metropolitan bao gồm 4 tiểu khu là The Zurich, The Paris, The London và The Beverly , tổng số 15 tòa căn hộ phân khúc cao cấp với các tiêu chuẩn bàn giao nội thất và dịch vụ quản lý vận hành đẳng cấp bậc nhất tại dự án.	The Ocean View : tương ứng với 3 phong cách khách nhau là: The Zenpark : 4 tòa căn hộ cao cấp Nhật Bản, đã hoàn thiện và bàn giao.	\N	1	t	2026-07-07 12:02:52.552701+00	2026-07-07 12:02:52.552701+00
2	the-zenpark	The Zenpark	The Zenpark là khu căn hộ cao cấp bậc nhất tại “Quận Ocean” thuộc phân khúc Ruby với tiêu chuẩn bàn giao và chất lượng dịch vụ quản lý vận hành tương đương với các khu căn hộ Vinhomes Times City, Vinhomes Royal City, Vinhomes Symphony,… Căn hộ The Zenpark là không gian sống đẳng cấp, tiện nghi và bình yên mang đậm phong cách Nhật Bản.\n\nKhu chung cư The Zenpark được kiến tạo trên ý tưởng về một lối sống cân bằng thăng hoa được xây đắp từ triết lý sống đến từ Nhật Bản, nơi các giá trị dẫn lối tương lai, là mạch nguồn khai mở thịnh vượng, mang đến sự an yên, hài hòa từ thể chất đến tinh thần. Tại đây, cư dân có thể cảm nhận sự bình yên và trải nghiệm những khoảnh khắc trọn vẹn quý giá tại vườn Nhật duy nhất của Đại đô thị Vinhomes Ocean Park.\n\nQuy mô : 04 tòa cao 31 tầng là R1.01 , R1.02 , R1.03 và R1.05 ; 01 Hầm thông nhau rộng 24.000m2.\n\nSố lượng căn hộ: Hơn 2.500 căn hộ cao cấp.	Tiểu khu The Zenpark sở hữu vị trí đắc địa bậc nhất của Đại đô thị Vinhomes Ocean Park, giao thông vô cùng thuận tiện khi nằm kế cận với đường Lý Thánh Tông (rộng 40m) kết nối các trục đường huyết mạch là Đường 5 (cũ), Cao tốc Hà Nội – Hải Phòng và đường 379 đi Ecopark. Từ Zenpark, cư dân có thể kết nối cả nội và ngoại khu một cách dễ dàng.\n\nĐặc biệt, một trong những yếu tố đắt giá nhất của một Bất động sản là trong tương lai, cư dân Zenpark sẽ được thừa hưởng trực tiếp lợi ích từ tuyến đường sắt đô thị Metro số 8 nằm kế cận với phân khu.	Nhận nhà ngay.	\N	2	t	2026-07-07 12:02:52.552701+00	2026-07-07 12:02:52.552701+00
3	the-pavilion	The Pavilion	The Pavilion là phân khu căn hộ thuộc phân khu The Ocean View – trung tâm của khu đô thị Vinhomes Ocean Park. Sở hữu vị trí đắc địa, căn hộ The Pavilion sẽ là không gian sống tiện nghi, hiện đại và an lành cho mọi cư dân.\n\nPhân khu The Pavilion được mệnh danh là Ốc đảo xanh giữ lòng Thành phố Biển Ocean City với hệ sinh thái cây xanh, thảm cỏ, hồ nước và vườn thực vật Botanic Garden. Chỉ cần một bước chân là cư dân Pavilion có thể tận hưởng một không gian sống xanh và hít thở khí trời mát lành tựa như một ốc đảo nghỉ dưỡng Singapore ngay trước thềm nhà.\n\nThe Pavilion cũng là phân khu duy nhất sở hữu riêng cho mình 02 tầng hầm để xe thông nhau (các phân khu khác chỉ có 1 hầm) và nằm ngay bên cạnh Nhà để xe 4 tầng. Vì vậy mà cư dân sẽ không cần phải lo lắng về việc thiếu chỗ để xe ô tô khi về sinh sống tại đây.\n\nQuy mô : 04 tòa cao 30 – 32 tầng là P1, P2, P3 và P4.	The Pavilion là phân khu căn hộ thuộc phân khu The Ocean View – trung tâm của khu đô thị Vinhomes Ocean Park. Sở hữu vị trí đắc địa, căn hộ The Pavilion sẽ là không gian sống tiện nghi, hiện đại và an lành cho mọi cư dân.\n\nThe Pavilion cũng là phân khu duy nhất sở hữu riêng cho mình 02 tầng hầm để xe thông nhau (các phân khu khác chỉ có 1 hầm) và nằm ngay bên cạnh Nhà để xe 4 tầng. Vì vậy mà cư dân sẽ không cần phải lo lắng về việc thiếu chỗ để xe ô tô khi về sinh sống tại đây.	BÀN GIAO QUÝ 1 NĂM 2024 BẢNG GIÁ GỐC – THỦ TỤC TRỰC TIẾP CĐT Tư vấn ngay	\N	3	t	2026-07-07 12:02:52.552701+00	2026-07-07 12:02:52.552701+00
4	the-bayfront	The Bayfront	Vinhomes Ocean Park sở hữu hệ sinh thái tiện ích và dịch vụ mang thương hiệu Vinhomes vô cùng đa dạng và đẳng cấp. Sống tại Vinhomes Ocean Park, các cư dân tinh hoa sẽ được tận hưởng trọn vẹn một không gian tiện nghi và những phút giây hạnh phúc bên gia đình.\n\nPhòng kinh doanh dự án Vinhomes Ocean Park.\n\nĐịa chỉ giao dịch: The Galleria by Masterise Homes, Vinhomes Ocean Park, Gia Lâm, Hà Nội.\n\nThe Ocean View The Zenpark Tòa R1.01	Đang cập nhật	Đang cập nhật	\N	4	t	2026-07-07 12:02:52.552701+00	2026-07-07 12:02:52.552701+00
5	the-zurich	The Zurich	The Zurich là tiểu khu căn hộ đầu tiên thuộc phân khu The Metropolitan Vinhomes Ocean Park được mở bán. Được quy hoạch và xây dựng dựa trên cảm hứng từ “giá trị vô giá của thời gian” với phong cách kiến trúc Thụy Sỹ, căn hộ The Zurich mang vẻ đẹp đầy kiêu hãnh giữa “tâm điểm thượng lưu” cửa ngõ của “Thành phố biển Ocean City”.\n\nPhân khu The Zurich nằm tại vị trí cửa ngõ của dự án Vinhomes Ocean Park, nằm kế cận với các trục đường huyết mạch là đường Đại Dương (đường chính dẫn vào dự án từ cổng), đường Lý Thánh Tông 40m và đường cao tốc Hà Nội – Hải Phòng. Trong tương lai, đây cũng là vị trí vô cùng thuận tiện để kết nối với tuyến đường sắt đô thị Metro khi nằm ngay gần với nhà ga của tuyến Metro số 08 và các điểm xe bus điện Vinbus.\n\nThe Zurich nằm ngay bên cạnh với Công viên hồ San Hô rộng lớn với không gian cây xanh, mặt nước và hệ sinh thái tiện ích ngoài trời đa dạng như BBQ, Gym, sân chơi liên hoàn, … Bên cạnh đó, phân khu cũng được bao quanh bởi hệ thống giáo dục chất lượng cao với trường quốc tế Brighton College, Deway và trường liên cấp Vinschool.\n\nCăn hộ The Zurich được thiết kế tối ưu hóa về công năng sử dụng với không gian nội thất sang trọng và tinh tế. Thiết kế thông mình với những mảng kính cửa sổ và cửa ban công rộng lớn giúp mọi phòng đều tràn ngập ánh sáng và khí trời tự nhiên.	The Zurich là tiểu khu căn hộ đầu tiên thuộc phân khu The Metropolitan Vinhomes Ocean Park được mở bán. Được quy hoạch và xây dựng dựa trên cảm hứng từ “giá trị vô giá của thời gian” với phong cách kiến trúc Thụy Sỹ, căn hộ The Zurich mang vẻ đẹp đầy kiêu hãnh giữa “tâm điểm thượng lưu” cửa ngõ của “Thành phố biển Ocean City”.\n\nPhân khu The Zurich nằm tại vị trí cửa ngõ của dự án Vinhomes Ocean Park, nằm kế cận với các trục đường huyết mạch là đường Đại Dương (đường chính dẫn vào dự án từ cổng), đường Lý Thánh Tông 40m và đường cao tốc Hà Nội – Hải Phòng. Trong tương lai, đây cũng là vị trí vô cùng thuận tiện để kết nối với tuyến đường sắt đô thị Metro khi nằm ngay gần với nhà ga của tuyến Metro số 08 và các điểm xe bus điện Vinbus.	dự kiến tháng 8 năm 2025.	\N	5	t	2026-07-07 12:02:52.552701+00	2026-07-07 12:02:52.552701+00
6	the-beverly	The Beverly	The Beverly là tiểu khu căn hộ thứ 2 thuộc phân khu The Metropolitan được mở bán tiếp theo sau khu The Zurich . The Beverly là “mảnh ghép chất Mỹ” duy nhất tại tâm điểm thượng lưu của “Quận trung tâm” Ocean City.\n\nLấy cảm hứng từ Beverly Hills danh giá xa hoa, khu căn hộ The Beverly với cảnh quan và thiết kế phóng khoáng đậm chất Mỹ đem tới phong cách Glory Living – dành cho các chủ nhân yêu thích lối sống hiện đại, nổi bật và tỏa sáng.\n\nPhân khu The Beverly sở hữu vị trí “độc tôn” khi nằm kế cận với Quảng trường ga Metro của tuyến Metro số 8 – đường Lý Thánh Tông. Phân khu cũng nằm ngay trên các tuyến xe bus điện Vinbus nội và ngoại khu với các mặt đường Hải Đăng 3, Hải Đăng 8 và Hải Đăng 5 .\n\nTừ phân khu, cư dân có thể dễ dàng di chuyển tới các tiện ích nội khu đô thị như Hồ Ngọc Trai, Biển nhân tạo hay Trung tâm thương mại Vincom Mega Mall hay nhanh chóng kết nối với đường Lý Thánh Tông để từ di chuyển tới Cao tốc Hà Nội – Hải Phòng và quốc lộ 5A.	The Beverly là tiểu khu căn hộ thứ 2 thuộc phân khu The Metropolitan được mở bán tiếp theo sau khu The Zurich . The Beverly là “mảnh ghép chất Mỹ” duy nhất tại tâm điểm thượng lưu của “Quận trung tâm” Ocean City.\n\nPhân khu The Beverly sở hữu vị trí “độc tôn” khi nằm kế cận với Quảng trường ga Metro của tuyến Metro số 8 – đường Lý Thánh Tông. Phân khu cũng nằm ngay trên các tuyến xe bus điện Vinbus nội và ngoại khu với các mặt đường Hải Đăng 3, Hải Đăng 8 và Hải Đăng 5 .	Dự kiến quý 3/2026.	\N	6	t	2026-07-07 12:02:52.552701+00	2026-07-07 12:02:52.552701+00
7	the-london	The London	The London là phân khu căn hộ chung cư mới nhất được mở bán tại Vinhomes Ocean Park, nối tiếp sự thành công của phân khu The Beverly . Căn hộ The London được thiế kế theo phong cách lấy cảm hứng thì kiến trúc cổ kính và sang trọng của thành phố London xinh đẹp.\n\nPhân khu The London sở hữu vị trí đắc địa khi nằm tại vị trí 3 mặt đường chính là đường Lý Thánh Tông, đường Hải Đăng 8 và đường Hải Đăng 5.\n\nTừ phân khu London, cư dân có thể nhanh chóng kết nối với cao tốc Hà Nội – Hải Phòng với Quốc lộ 5 qua đường Lý Thánh Tông để qua đó di chuyển vào Trung tâm thành phố Hà Nộ và các tỉnh lân cận. Cư dân London cũng có thể dễ dàng tiếp cận với các Đại tiện ích của khu đô thị như Hồ Ngọc Trai trung tâm, Biển nhân tạo, Đại họ Vinuni, Vincom Mega Mall, Trường liên cấp Vinschool, … qua 2 trục đoừng nội khu là Hải Đăng 5 và Hải Đăng 8.\n\nTỔNG MẶT BẰNG THE LONDON VINHOMES OCEAN PARK MẶT BẰNG CĂN HỘ THE LONDON Phân khu The London Vinhomes Ocean Park bao gồm 3 tòa căn hộ ký hiệu là LD1, LD2 và LD3 với chiều cao 26 tầng và mật độ 17 – 20 căn/tầng. Các tòa căn hộ có thiết kế mặt cắt hình chữ Z, T và U giúp tăng tối da diện tích tiếp xúc với không gian tự nhiên từ mọi mặt của tòa nhà.	Phân khu The London sở hữu vị trí đắc địa khi nằm tại vị trí 3 mặt đường chính là đường Lý Thánh Tông, đường Hải Đăng 8 và đường Hải Đăng 5.\n\nTừ phân khu London, cư dân có thể nhanh chóng kết nối với cao tốc Hà Nội – Hải Phòng với Quốc lộ 5 qua đường Lý Thánh Tông để qua đó di chuyển vào Trung tâm thành phố Hà Nộ và các tỉnh lân cận. Cư dân London cũng có thể dễ dàng tiếp cận với các Đại tiện ích của khu đô thị như Hồ Ngọc Trai trung tâm, Biển nhân tạo, Đại họ Vinuni, Vincom Mega Mall, Trường liên cấp Vinschool, … qua 2 trục đoừng nội khu là Hải Đăng 5 và Hải Đăng 8.	Quý 3/2026.	\N	7	t	2026-07-07 12:02:52.552701+00	2026-07-07 12:02:52.552701+00
8	the-paris	The Paris	The Paris là khu căn hộ cuối cùng thuộc phân khu The Metropolitan được mở bán tại khu đô thị Vinhomes Ocean Park. Là một trong những mảnh ghép cuối cùng hoàn thiện Thành phố biển, căn hộ The Paris thực sự là không gian sống hiện đại, đẳng cấp và vô cùng tiện nghi.\n\nNằm tại cửa ngõ của Đại đô thị Vinhomes Ocean Park , phân khu The Paris sở hữu vị trí đắc địa bậc nhất dự án với kết nối giao thông thuận tiện, cùng hệ sinh thái tiện ích đa dạng và đẳng cấp.\n\nVị trí đắt giá của The Paris còn được thể hiện khi nằm kế cận với tuyến đường Đại Dương (trục giao thông chính dẫn vào dự án Vinhomes Ocean Park) với các tuyến xe bus điện xanh Vinbus và đường Lý Thánh Tông (tuyến Metro số 08 trong tương lai). Từ phân khu căn hộ, cư dân có thể dễ dàng kết nối với đường cao tốc Hà Nội – Hải Phòng và Quốc lộ 5A để qua đó di chuyển vào trung tâm Hà Nội và các tỉnh thành lân cận.\n\nLợi thế về vị trí cũng giúp cho The Paris được bao quanh bởi hệ thống giáo dục chất lượng cao như trường liên cấp Vinschool, trường quốc tế Brighton College, Deway và nhiều trường học đang tiếp tục được xây dựng. Cư dân The Paris cũng được tận hưởng không gian xanh khoáng đạt và trong lành cùng hệ tiện ích đa dạng của Công viên hồ San Hô nằm kế cận.	The Paris là khu căn hộ cuối cùng thuộc phân khu The Metropolitan được mở bán tại khu đô thị Vinhomes Ocean Park. Là một trong những mảnh ghép cuối cùng hoàn thiện Thành phố biển, căn hộ The Paris thực sự là không gian sống hiện đại, đẳng cấp và vô cùng tiện nghi.\n\nNằm tại cửa ngõ của Đại đô thị Vinhomes Ocean Park , phân khu The Paris sở hữu vị trí đắc địa bậc nhất dự án với kết nối giao thông thuận tiện, cùng hệ sinh thái tiện ích đa dạng và đẳng cấp.	Đang cập nhật	\N	8	t	2026-07-07 12:02:52.552701+00	2026-07-07 12:02:52.552701+00
9	the-palma	The Palma	Các loại hình phát triển : Căn hộ Studio, 1PN, 1PN+, 2PN, 2PN+, 3PN, 3PN (thang máy riêng), Duplex, Penthouse và Penthouse Duplex (thang máy riêng).\n\nDiện tích : 28,6 – 93,9m2 (Studio – 3PN).\n\nTầng tiện ích : Tầng 1 và tần 13.\n\nPháp lý : Sở hữu không thời hạn.	Phân khu The Palma sở hữu vị trí khoáng đạt với cả 4 mặt của các tòa căn hộ đều sở hữu tầm view rộng mở toàn cảnh Thành phố biển Ocean Park. Phân khu sở hữu 3 mặt tiền đường là Biển Hồ 1, Biển Hồ 2 và đặc biệt là trục giao thông huyết mạch Biển Hồ kết nối đường Lý Thánh Tông với Đại lộ 52m và Hồ Ngọc Trai 24,5ha.\n\nVị trí của khu đất 2 tòa căn hộ The Palma 1 và The Palma 2 phân khu The Palma:	Từ Quý 3/2027.	\N	9	t	2026-07-07 12:02:52.552701+00	2026-07-07 12:02:52.552701+00
10	masteri-waterfront	Masteri Waterfront	Masteri Waterfront là dự án căn hộ hạng sang nằm trong quần thể đại đô thị Vinhomes Ocean Park , Gia Lâm, Hà Nội. Được phát triển bởi Masterise Homes – nhà phát triển bất động sản uy tín hàng đầu Việt Nam, dự án sở hữu vị trí độc tôn tại trung tâm của khu đô thị với thiết kế sang trọng và hệ thống tiện ích & dịch vụ đẳng cấp, mang đến cho cư dân không gian sống hoàn hảo, đáp ứng mọi nhu cầu sinh hoạt, giải trí và nghỉ dưỡng của các chủ nhân thương lưu.\n\nLoại hình : Studio, 1 ngủ + 1, 2 ngủ, 2 ngủ + 1, 3 ngủ.\n\nBàn giao : Quý 3/2023 – Quý 4/2024.\n\nQuà tặng: 12 tháng phí dịch vụ.	Masteri Waterfront là dự án căn hộ hạng sang nằm trong quần thể đại đô thị Vinhomes Ocean Park , Gia Lâm, Hà Nội. Được phát triển bởi Masterise Homes – nhà phát triển bất động sản uy tín hàng đầu Việt Nam, dự án sở hữu vị trí độc tôn tại trung tâm của khu đô thị với thiết kế sang trọng và hệ thống tiện ích & dịch vụ đẳng cấp, mang đến cho cư dân không gian sống hoàn hảo, đáp ứng mọi nhu cầu sinh hoạt, giải trí và nghỉ dưỡng của các chủ nhân thương lưu.\n\nMasteri Waterfront tọa lạc tại vị trí trung tâm “Quận Biển” Vinhomes Ocean Park, được ví như trái tim của đại đô thị, nơi hội tụ mọi tiện ích và cảnh quan đẳng cấp. Sở hữu vị trí đắc địa, Masteri Waterfront Ocean Park mang đến cho cư dân không gian sống lý tưởng, kết nối hoàn hảo với mọi nhu cầu sinh hoạt, giải trí và nghỉ dưỡng.	Quý 3/2023 – Quý 4/2024.	\N	10	t	2026-07-07 12:02:52.552701+00	2026-07-07 12:02:52.552701+00
11	masteri-lakeside	Masteri Lakeside	Masteri Lakeside là dự án cuối cùng thuộc bộ sưu tập căn hộ Masteri Collection và là một trong những mảnh ghép hoàn thiện Thành phố biển Vinhomes Ocean Park, Gia Lâm, Hà Nội. Sở hữu thiết kế hiện đại, nội thất sang trọng và hệ tiện ích chuẩn mực, căn hộ Masteri Lakeside thực sự là không gian sống đẳng cấp và tiện nghi bậc nhất tại Đại đô thị Ocean City.\n\nDự án Masteri Lakeside tọa lạc tại giao điểm của đường Lý Thánh Tông và Đại Tây Dương, từ dự án, cư dân có thể dễ dàng kết nối các Đại tiện ích của toàn Ocean City, trung tâm Thủ đô Hà Nội và các vùng kinh tế trọng điểm Bắc Bộ với hạ tầng giao thông đường bộ hiện đại vượt bậc.\n\nVỊ TRÍ CÁC TÒA CĂN HỘ MASTERI LAKESIDE Masteri Lakeside Ocean Park bao gồm 3 tòa căn hộ cao từ 34 – 38 tầng trên tổng diện tích đất 17.930m2 và mật độ xây dựng chỉ hơn 30%. Các tòa căn hộ được được thiết kế với kiến trúc mặt ngoài sang trọng nổi bật vỡi những mảng kính Low-E cao cấp, hình thái tòa nhà thanh gọn, vững chắc giúp mở rộng tối đa tầm nhìn toàn cảnh Thành phố biển hồ và Công viên hồ điều hòa xanh khoáng đạt.\n\nCác căn hộ Masteri Lakeside được thiết kế theo phong cách hiện đại, layout căn hộ hài hòa với ban công rộng và các mảng cửa kính lớn giúp không gian bên trong luôn ngập tràn ánh sáng và khí trời tự nhiên. Các vật liệu, thiết bị hoàn thiện trong căn hộ đều đến từ những thương hiệu nổi tiếng thế giới với độ bền bỉ và tính thẩm mĩ cao, giúp mang đến sự tiện nghi và trải nghiệm xứng tầm cho gia chủ.	Dự án Masteri Lakeside tọa lạc tại giao điểm của đường Lý Thánh Tông và Đại Tây Dương, từ dự án, cư dân có thể dễ dàng kết nối các Đại tiện ích của toàn Ocean City, trung tâm Thủ đô Hà Nội và các vùng kinh tế trọng điểm Bắc Bộ với hạ tầng giao thông đường bộ hiện đại vượt bậc.\n\nVỊ TRÍ CÁC TÒA CĂN HỘ MASTERI LAKESIDE Masteri Lakeside Ocean Park bao gồm 3 tòa căn hộ cao từ 34 – 38 tầng trên tổng diện tích đất 17.930m2 và mật độ xây dựng chỉ hơn 30%. Các tòa căn hộ được được thiết kế với kiến trúc mặt ngoài sang trọng nổi bật vỡi những mảng kính Low-E cao cấp, hình thái tòa nhà thanh gọn, vững chắc giúp mở rộng tối đa tầm nhìn toàn cảnh Thành phố biển hồ và Công viên hồ điều hòa xanh khoáng đạt.	Quý 4/2026.	\N	11	t	2026-07-07 12:02:52.552701+00	2026-07-07 12:02:52.552701+00
12	the-senique-hanoi	The Senique Hanoi	The Senique Hanoi là khu căn hộ cao cấp tọa lạc tại vị trí “trái tim” khu đô thị Vinhomes Ocean Park với không gian sống hòa quyện cùng cảnh quan xanh và hồ nước rộng mở. Là khu căn hộ được quản lý theo mô hình khu “ Compound ” khép kín đầu tiên và duy nhất tại Ocean Park, The Senique Hà Nội sở hữu không gian sống riêng tư và an ninh tuyệt đối với hệ sinh thái tiện ích đặc quyền vô cùng đẳng cấp.\n\nChủ đầu tư : Công ty Cổ phần đầu tư phát triển kinh doanh Bình Minh (Thành viên của CapitaLand Development).\n\nQuy mô: 3 tòa The Senique 1, The Senique 2 và The Senique Premier, chiều cao 37 tầng với 2.152 căn hộ.\n\n* Ghi chú : Giá bán căn hộ chung cư The Senique sẽ thay đổi tùy vào từng giai đoạn mở bán, vị trí tòa, khoảng tầng và hướng ban công.	The Senique Hanoi là khu căn hộ cao cấp tọa lạc tại vị trí “trái tim” khu đô thị Vinhomes Ocean Park với không gian sống hòa quyện cùng cảnh quan xanh và hồ nước rộng mở. Là khu căn hộ được quản lý theo mô hình khu “ Compound ” khép kín đầu tiên và duy nhất tại Ocean Park, The Senique Hà Nội sở hữu không gian sống riêng tư và an ninh tuyệt đối với hệ sinh thái tiện ích đặc quyền vô cùng đẳng cấp.\n\n* Ghi chú : Giá bán căn hộ chung cư The Senique sẽ thay đổi tùy vào từng giai đoạn mở bán, vị trí tòa, khoảng tầng và hướng ban công.	Quý 2 năm 2027.	\N	12	t	2026-07-07 12:02:52.552701+00	2026-07-07 12:02:52.552701+00
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: ocean_app
--

COPY public.users (id, email, full_name, password_hash, role, is_active, created_at, updated_at, avatar_url, experience_years, achievements, is_deleted) FROM stdin;
1	admin@oceanpark.vn	Quản trị Ocean Park	$argon2id$v=19$m=65536,t=3,p=4$rYR6ojMO4iEPEW9QChvJSQ$G/z2i1/zwOJd5+5OkAB+sR8f5+4PsnYyj6Pwpo7O2SU	admin	t	2026-07-07 12:02:52.977261+00	2026-07-07 12:02:52.977261+00	\N	0	\N	f
\.


--
-- Name: amenities_id_seq; Type: SEQUENCE SET; Schema: public; Owner: ocean_app
--

SELECT pg_catalog.setval('public.amenities_id_seq', 438, true);


--
-- Name: apartment_specs_id_seq; Type: SEQUENCE SET; Schema: public; Owner: ocean_app
--

SELECT pg_catalog.setval('public.apartment_specs_id_seq', 134, true);


--
-- Name: conversations_id_seq; Type: SEQUENCE SET; Schema: public; Owner: ocean_app
--

SELECT pg_catalog.setval('public.conversations_id_seq', 1, false);


--
-- Name: customer_accounts_id_seq; Type: SEQUENCE SET; Schema: public; Owner: ocean_app
--

SELECT pg_catalog.setval('public.customer_accounts_id_seq', 1, false);


--
-- Name: customer_notes_id_seq; Type: SEQUENCE SET; Schema: public; Owner: ocean_app
--

SELECT pg_catalog.setval('public.customer_notes_id_seq', 1, false);


--
-- Name: fallback_rules_id_seq; Type: SEQUENCE SET; Schema: public; Owner: ocean_app
--

SELECT pg_catalog.setval('public.fallback_rules_id_seq', 1, false);


--
-- Name: messages_id_seq; Type: SEQUENCE SET; Schema: public; Owner: ocean_app
--

SELECT pg_catalog.setval('public.messages_id_seq', 1, false);


--
-- Name: sales_policies_id_seq; Type: SEQUENCE SET; Schema: public; Owner: ocean_app
--

SELECT pg_catalog.setval('public.sales_policies_id_seq', 80, true);


--
-- Name: sales_scopes_id_seq; Type: SEQUENCE SET; Schema: public; Owner: ocean_app
--

SELECT pg_catalog.setval('public.sales_scopes_id_seq', 1, false);


--
-- Name: subdivisions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: ocean_app
--

SELECT pg_catalog.setval('public.subdivisions_id_seq', 12, true);


--
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: ocean_app
--

SELECT pg_catalog.setval('public.users_id_seq', 1, true);


--
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: public; Owner: ocean_app
--

ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


--
-- Name: amenities amenities_pkey; Type: CONSTRAINT; Schema: public; Owner: ocean_app
--

ALTER TABLE ONLY public.amenities
    ADD CONSTRAINT amenities_pkey PRIMARY KEY (id);


--
-- Name: apartment_specs apartment_specs_pkey; Type: CONSTRAINT; Schema: public; Owner: ocean_app
--

ALTER TABLE ONLY public.apartment_specs
    ADD CONSTRAINT apartment_specs_pkey PRIMARY KEY (id);


--
-- Name: apartment_specs apartment_specs_subdivision_id_unit_type_key; Type: CONSTRAINT; Schema: public; Owner: ocean_app
--

ALTER TABLE ONLY public.apartment_specs
    ADD CONSTRAINT apartment_specs_subdivision_id_unit_type_key UNIQUE (subdivision_id, unit_type);


--
-- Name: conversations conversations_pkey; Type: CONSTRAINT; Schema: public; Owner: ocean_app
--

ALTER TABLE ONLY public.conversations
    ADD CONSTRAINT conversations_pkey PRIMARY KEY (id);


--
-- Name: conversations conversations_session_id_key; Type: CONSTRAINT; Schema: public; Owner: ocean_app
--

ALTER TABLE ONLY public.conversations
    ADD CONSTRAINT conversations_session_id_key UNIQUE (session_id);


--
-- Name: customer_accounts customer_accounts_phone_key; Type: CONSTRAINT; Schema: public; Owner: ocean_app
--

ALTER TABLE ONLY public.customer_accounts
    ADD CONSTRAINT customer_accounts_phone_key UNIQUE (phone);


--
-- Name: customer_accounts customer_accounts_pkey; Type: CONSTRAINT; Schema: public; Owner: ocean_app
--

ALTER TABLE ONLY public.customer_accounts
    ADD CONSTRAINT customer_accounts_pkey PRIMARY KEY (id);


--
-- Name: customer_notes customer_notes_pkey; Type: CONSTRAINT; Schema: public; Owner: ocean_app
--

ALTER TABLE ONLY public.customer_notes
    ADD CONSTRAINT customer_notes_pkey PRIMARY KEY (id);


--
-- Name: fallback_rules fallback_rules_keyword_key; Type: CONSTRAINT; Schema: public; Owner: ocean_app
--

ALTER TABLE ONLY public.fallback_rules
    ADD CONSTRAINT fallback_rules_keyword_key UNIQUE (keyword);


--
-- Name: fallback_rules fallback_rules_pkey; Type: CONSTRAINT; Schema: public; Owner: ocean_app
--

ALTER TABLE ONLY public.fallback_rules
    ADD CONSTRAINT fallback_rules_pkey PRIMARY KEY (id);


--
-- Name: messages messages_pkey; Type: CONSTRAINT; Schema: public; Owner: ocean_app
--

ALTER TABLE ONLY public.messages
    ADD CONSTRAINT messages_pkey PRIMARY KEY (id);


--
-- Name: sales_policies sales_policies_pkey; Type: CONSTRAINT; Schema: public; Owner: ocean_app
--

ALTER TABLE ONLY public.sales_policies
    ADD CONSTRAINT sales_policies_pkey PRIMARY KEY (id);


--
-- Name: sales_scopes sales_scopes_pkey; Type: CONSTRAINT; Schema: public; Owner: ocean_app
--

ALTER TABLE ONLY public.sales_scopes
    ADD CONSTRAINT sales_scopes_pkey PRIMARY KEY (id);


--
-- Name: subdivisions subdivisions_pkey; Type: CONSTRAINT; Schema: public; Owner: ocean_app
--

ALTER TABLE ONLY public.subdivisions
    ADD CONSTRAINT subdivisions_pkey PRIMARY KEY (id);


--
-- Name: subdivisions subdivisions_slug_key; Type: CONSTRAINT; Schema: public; Owner: ocean_app
--

ALTER TABLE ONLY public.subdivisions
    ADD CONSTRAINT subdivisions_slug_key UNIQUE (slug);


--
-- Name: users users_email_key; Type: CONSTRAINT; Schema: public; Owner: ocean_app
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_email_key UNIQUE (email);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: ocean_app
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: ix_amenities_scope; Type: INDEX; Schema: public; Owner: ocean_app
--

CREATE INDEX ix_amenities_scope ON public.amenities USING btree (scope);


--
-- Name: ix_amenities_subdivision_id; Type: INDEX; Schema: public; Owner: ocean_app
--

CREATE INDEX ix_amenities_subdivision_id ON public.amenities USING btree (subdivision_id);


--
-- Name: ix_apartment_specs_subdivision_id; Type: INDEX; Schema: public; Owner: ocean_app
--

CREATE INDEX ix_apartment_specs_subdivision_id ON public.apartment_specs USING btree (subdivision_id);


--
-- Name: ix_conversations_customer_account_id; Type: INDEX; Schema: public; Owner: ocean_app
--

CREATE INDEX ix_conversations_customer_account_id ON public.conversations USING btree (customer_account_id);


--
-- Name: ix_conversations_session_id; Type: INDEX; Schema: public; Owner: ocean_app
--

CREATE UNIQUE INDEX ix_conversations_session_id ON public.conversations USING btree (session_id);


--
-- Name: ix_conversations_status; Type: INDEX; Schema: public; Owner: ocean_app
--

CREATE INDEX ix_conversations_status ON public.conversations USING btree (status);


--
-- Name: ix_customer_accounts_assigned_to_id; Type: INDEX; Schema: public; Owner: ocean_app
--

CREATE INDEX ix_customer_accounts_assigned_to_id ON public.customer_accounts USING btree (assigned_to_id);


--
-- Name: ix_customer_accounts_customer_type; Type: INDEX; Schema: public; Owner: ocean_app
--

CREATE INDEX ix_customer_accounts_customer_type ON public.customer_accounts USING btree (customer_type);


--
-- Name: ix_customer_accounts_is_active; Type: INDEX; Schema: public; Owner: ocean_app
--

CREATE INDEX ix_customer_accounts_is_active ON public.customer_accounts USING btree (is_active);


--
-- Name: ix_customer_accounts_phone; Type: INDEX; Schema: public; Owner: ocean_app
--

CREATE UNIQUE INDEX ix_customer_accounts_phone ON public.customer_accounts USING btree (phone);


--
-- Name: ix_customer_accounts_status; Type: INDEX; Schema: public; Owner: ocean_app
--

CREATE INDEX ix_customer_accounts_status ON public.customer_accounts USING btree (status);


--
-- Name: ix_customer_notes_author_id; Type: INDEX; Schema: public; Owner: ocean_app
--

CREATE INDEX ix_customer_notes_author_id ON public.customer_notes USING btree (author_id);


--
-- Name: ix_customer_notes_customer_account_id; Type: INDEX; Schema: public; Owner: ocean_app
--

CREATE INDEX ix_customer_notes_customer_account_id ON public.customer_notes USING btree (customer_account_id);


--
-- Name: ix_fallback_rules_is_active; Type: INDEX; Schema: public; Owner: ocean_app
--

CREATE INDEX ix_fallback_rules_is_active ON public.fallback_rules USING btree (is_active);


--
-- Name: ix_messages_conversation_created; Type: INDEX; Schema: public; Owner: ocean_app
--

CREATE INDEX ix_messages_conversation_created ON public.messages USING btree (conversation_id, created_at);


--
-- Name: ix_sales_policies_status; Type: INDEX; Schema: public; Owner: ocean_app
--

CREATE INDEX ix_sales_policies_status ON public.sales_policies USING btree (status);


--
-- Name: ix_sales_policies_subdivision_id; Type: INDEX; Schema: public; Owner: ocean_app
--

CREATE INDEX ix_sales_policies_subdivision_id ON public.sales_policies USING btree (subdivision_id);


--
-- Name: ix_sales_scopes_subdivision_id; Type: INDEX; Schema: public; Owner: ocean_app
--

CREATE INDEX ix_sales_scopes_subdivision_id ON public.sales_scopes USING btree (subdivision_id);


--
-- Name: ix_sales_scopes_user_id; Type: INDEX; Schema: public; Owner: ocean_app
--

CREATE INDEX ix_sales_scopes_user_id ON public.sales_scopes USING btree (user_id);


--
-- Name: ix_subdivisions_is_published; Type: INDEX; Schema: public; Owner: ocean_app
--

CREATE INDEX ix_subdivisions_is_published ON public.subdivisions USING btree (is_published);


--
-- Name: ix_subdivisions_slug; Type: INDEX; Schema: public; Owner: ocean_app
--

CREATE UNIQUE INDEX ix_subdivisions_slug ON public.subdivisions USING btree (slug);


--
-- Name: ix_users_email; Type: INDEX; Schema: public; Owner: ocean_app
--

CREATE UNIQUE INDEX ix_users_email ON public.users USING btree (email);


--
-- Name: ix_users_is_active; Type: INDEX; Schema: public; Owner: ocean_app
--

CREATE INDEX ix_users_is_active ON public.users USING btree (is_active);


--
-- Name: ix_users_is_deleted; Type: INDEX; Schema: public; Owner: ocean_app
--

CREATE INDEX ix_users_is_deleted ON public.users USING btree (is_deleted);


--
-- Name: ix_users_role; Type: INDEX; Schema: public; Owner: ocean_app
--

CREATE INDEX ix_users_role ON public.users USING btree (role);


--
-- Name: amenities amenities_subdivision_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ocean_app
--

ALTER TABLE ONLY public.amenities
    ADD CONSTRAINT amenities_subdivision_id_fkey FOREIGN KEY (subdivision_id) REFERENCES public.subdivisions(id) ON DELETE CASCADE;


--
-- Name: apartment_specs apartment_specs_subdivision_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ocean_app
--

ALTER TABLE ONLY public.apartment_specs
    ADD CONSTRAINT apartment_specs_subdivision_id_fkey FOREIGN KEY (subdivision_id) REFERENCES public.subdivisions(id) ON DELETE CASCADE;


--
-- Name: conversations conversations_subdivision_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ocean_app
--

ALTER TABLE ONLY public.conversations
    ADD CONSTRAINT conversations_subdivision_id_fkey FOREIGN KEY (subdivision_id) REFERENCES public.subdivisions(id) ON DELETE SET NULL;


--
-- Name: customer_notes customer_notes_author_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ocean_app
--

ALTER TABLE ONLY public.customer_notes
    ADD CONSTRAINT customer_notes_author_id_fkey FOREIGN KEY (author_id) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: customer_notes customer_notes_customer_account_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ocean_app
--

ALTER TABLE ONLY public.customer_notes
    ADD CONSTRAINT customer_notes_customer_account_id_fkey FOREIGN KEY (customer_account_id) REFERENCES public.customer_accounts(id) ON DELETE CASCADE;


--
-- Name: conversations fk_conversations_customer_account_id_customer_accounts; Type: FK CONSTRAINT; Schema: public; Owner: ocean_app
--

ALTER TABLE ONLY public.conversations
    ADD CONSTRAINT fk_conversations_customer_account_id_customer_accounts FOREIGN KEY (customer_account_id) REFERENCES public.customer_accounts(id) ON DELETE SET NULL;


--
-- Name: messages messages_conversation_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ocean_app
--

ALTER TABLE ONLY public.messages
    ADD CONSTRAINT messages_conversation_id_fkey FOREIGN KEY (conversation_id) REFERENCES public.conversations(id) ON DELETE CASCADE;


--
-- Name: sales_policies sales_policies_subdivision_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ocean_app
--

ALTER TABLE ONLY public.sales_policies
    ADD CONSTRAINT sales_policies_subdivision_id_fkey FOREIGN KEY (subdivision_id) REFERENCES public.subdivisions(id) ON DELETE CASCADE;


--
-- Name: sales_scopes sales_scopes_subdivision_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ocean_app
--

ALTER TABLE ONLY public.sales_scopes
    ADD CONSTRAINT sales_scopes_subdivision_id_fkey FOREIGN KEY (subdivision_id) REFERENCES public.subdivisions(id) ON DELETE CASCADE;


--
-- Name: sales_scopes sales_scopes_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ocean_app
--

ALTER TABLE ONLY public.sales_scopes
    ADD CONSTRAINT sales_scopes_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- PostgreSQL database dump complete
--

\unrestrict rheOm5cfkb8eOtxYJGDhPp24omtJikJp30atoio2FJVJTuYzgCTg8AnPhsxlFuw

