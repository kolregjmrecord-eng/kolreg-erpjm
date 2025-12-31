if not firebase_admin._apps:
    try:
        # Hum local file ke bajaye Streamlit Secrets use kar rahe hain
        fb_dict = dict(st.secrets["firebase"])
        cred = credentials.Certificate(fb_dict)
        firebase_admin.initialize_app(cred)
    except Exception as e:
        st.error(f"Firebase connect nahi hua: {e}")

db = firestore.client()

# --- 2. CLOUD FUNCTIONS ---
def load_data(center, month):
    doc_id = f"{center}_{month}".replace(" ", "_")
    doc_ref = db.collection("jamiat_erp_final").document(doc_id)
    doc = doc_ref.get()
    return doc.to_dict() if doc.exists else {}

def load_fixed(center):
    doc = db.collection("fixed_assets").document(center).get()
    return doc.to_dict() if doc.exists else {"ramzan": 0, "telethon": 0}

def save_data(center, month, d):
    doc_id = f"{center}_{month}".replace(" ", "_")
    db.collection("jamiat_erp_final").document(doc_id).set(d)
    return True

# --- 3. ALL 17 USERS DATABASE ---
USER_DB = {
    "admin@jamiat.com": {"name": "ADMIN PORTAL JAMIATUL MADINA KOLKATA REGION", "role": "admin", "title": "Rukne Majlis", "pass": "admin786"},
    "tu.kolkataregion@gmail.com": {"name": "Jamiatul Madina Kolkata", "role": "nazim", "title": "Nazim", "pass": "jamiat123"},
    "jamiasilchar01@gmail.com": {"name": "Jamiatul Madina Silchar", "role": "nazim", "title": "Nazim", "pass": "jamiat123"},
    "jamiatulmadinaasansol@gmail.com": {"name": "Jamiatul Madina Asansole", "role": "nazim", "title": "Nazim", "pass": "jamiat123"},
    "jamiatulmadinakhizarpur@gmail.com": {"name": "Jamiatul Madina Khidderpore", "role": "nazim", "title": "Nazim", "pass": "jamiat123"},
    "kolkatajamia01@gmail.com": {"name": "Jamiatul Madina Matiaburuz", "role": "nazim", "title": "Nazim", "pass": "jamiat123"},
    "jamiajamshedpur@gmail.com": {"name": "Jamiatul Madina Jamshedpur", "role": "nazim", "title": "Nazim", "pass": "jamiat123"},
    "jamiatulmadinadhanbaad@gmail.com": {"name": "Jamiatul Madina Dhanbad", "role": "nazim", "title": "Nazim", "pass": "jamiat123"},
    "ranchijamia@gmail.com": {"name": "Jamiatul Madina Ranchi", "role": "nazim", "title": "Nazim", "pass": "jamiat123"},
    "jamiasoro@gmail.com": {"name": "Jamiatul Madina Soro", "role": "nazim", "title": "Nazim", "pass": "jamiat123"},
    "jamiabhadrak@gmail.com": {"name": "Jamiatul Madina Bhadrak", "role": "nazim", "title": "Nazim", "pass": "jamiat123"},
    "medukolkataregion@gmail.com": {"name": "CHAND SIR", "role": "zimmadar", "title": "REGION ASRI ZIMMADAR", "pass": "jamiat123"},
    "jtmqiraatkolkataregion@gmail.com": {"name": "AQBAR RAZA", "role": "zimmadar", "title": "REGION SHOBA QIRAT ZIMMADAR", "pass": "jamiat123"},
    "rpkolkataregion26@gmail.com": {"name": "BAHAUDDIN MADANI", "role": "zimmadar", "title": "REGION PROMOTER", "pass": "jamiat123"},
    "jtmwestbengalassam@gmail.com": {"name": "BAHAUDDIN MADANI", "role": "zimmadar", "title": "STATE NAZIM E AALA", "pass": "jamiat123"},
    "tu.kolkataregion_zim@gmail.com": {"name": "SHABBIR ALI", "role": "zimmadar", "title": "REGION TALEEMI UMOOR ZIMMADAR", "pass": "jamiat123"},
    "preppclasskolkataregion@gmail.com": {"name": "BAQAR KHAN", "role": "zimmadar", "title": "REGION PREP CLASS", "pass": "jamiat123"},
}

st.set_page_config(page_title="Jamiat ERP", layout="wide")

st.markdown("""<style>
    div.stButton > button:first-child { background-color: #d9534f; color: white; border-radius: 8px; font-weight: bold; height: 45px; }
    .header-box { background: white; padding: 20px; border-radius: 15px; border: 2px solid #1a938a; margin-bottom: 10px; }
    .stat-box { background: #f8f9fa; padding: 10px; border-radius: 10px; border-left: 5px solid #1a938a; text-align: center; }
    .section-head { background: #1a938a; padding: 10px; border-radius: 5px; font-weight: bold; color: white; margin-top: 20px; }
    label p { color: #000000 !important; font-weight: bold !important; font-size: 16px !important; }
</style>""", unsafe_allow_html=True)

if 'user_info' not in st.session_state:
    st.markdown("<br><br>", unsafe_allow_html=True)
    c1, col2, c3 = st.columns([1, 1.5, 1])
    with col2:
        with st.container(border=True):
            st.markdown("<h4 style='text-align:center;'>JAMIATUL MADINA KOLKATA REGION ERP</h4>", unsafe_allow_html=True)
            l_type = st.radio("Select Login Type:", ["USER LOGIN", "ZIMMDAR LOGIN", "ADMIN LOGIN"], horizontal=True)
            u_email = st.text_input("Email Address")
            u_pass = st.text_input("Password", type="password")
            if st.button("LOG IN", use_container_width=True):
                if u_email in USER_DB and USER_DB[u_email]["pass"] == u_pass:
                    st.session_state['user_info'] = USER_DB[u_email]
                    st.rerun()
                else: st.error("Invalid Credentials")
else:
    user = st.session_state['user_info']
    sel_date = st.date_input("Select Month", value=datetime.now())
    m_key = sel_date.strftime("%B %Y")
    
    j_list = sorted([v["name"] for k,v in USER_DB.items() if v["role"]=="nazim"])
    target = st.selectbox("Select Jamia Center", j_list) if user['role'] == 'admin' else user['name']

    data = load_data(target, m_key)
    def v(k): return float(data.get(k, 0.0))

    can_edit = True if user['role'] == 'admin' else False

    t_exp = sum([v('salary'), v('rent'), v('electric'), v('kitchen'), v('travel'), v('other_exp')])
    t_inc = sum([v('gsb'), v('mab'), v('dp_cash'), v('dp_ashiya'), v('staff_cash'), v('staff_ashiya'), v('ramzan_inc'), v('telethone_inc')])
    total_p = v('staff_count') + v('student_count')
    per_head = t_exp / total_p if total_p > 0 else 0.0
    deficit = t_inc - t_exp
    pct = (t_inc / t_exp * 100) if t_exp > 0 else 0.0

    st.markdown(f'<div class="header-box">', unsafe_allow_html=True)
    h1, h2, h3, h4 = st.columns([2, 1, 1, 1])
    h1.markdown(f"<h1>{user['name']}</h1><p>{user['title']}</p>", unsafe_allow_html=True)
    h2.markdown(f'<div class="stat-box"><b>STAFF</b><br><h3>{int(v("staff_count"))}</h3></div>', unsafe_allow_html=True)
    h3.markdown(f'<div class="stat-box"><b>STUDENTS</b><br><h3>{int(v("student_count"))}</h3></div>', unsafe_allow_html=True)
    h4.markdown(f'<div class="stat-box"><b>PER HEAD</b><br><h3>₹{per_head:.2f}</h3></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("### 📊 Monthly Overview")
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Total Kharch", f"₹{t_exp:,.2f}")
    k2.metric("Total Aamdani", f"₹{t_inc:,.2f}")
    k3.metric("Bachat/Kami", f"₹{deficit:,.2f}", delta=deficit)
    k4.metric("Performance %", f"{pct:.1f}%")

    st.divider()

    if 'tab' not in st.session_state: st.session_state['tab'] = 'jamia'
    col_b1, col_b2, col_b3, col_b4 = st.columns(4)
    if col_b1.button("🏫 JAMIA DATA", use_container_width=True): st.session_state['tab'] = 'jamia'
    if col_b2.button("👤 ZIMMADAR", use_container_width=True): st.session_state['tab'] = 'zimmadar'
    if col_b3.button("🌎 REGION", use_container_width=True): st.session_state['tab'] = 'region'
    if col_b4.button("📊 REPORTS", use_container_width=True): st.session_state['tab'] = 'reports'

    if st.session_state['tab'] == 'jamia':
        if user['role'] in ['nazim', 'admin']:
            with st.form("jamia_form"):
                st.markdown('<div class="section-head">👥 STAFF & STUDENTS</div>', unsafe_allow_html=True)
                c1, c2 = st.columns(2)
                sc = c1.number_input("Total Staff", value=int(v('staff_count')), disabled=not can_edit)
                stc = c2.number_input("Total Students", value=int(v('student_count')), disabled=not can_edit)

                st.markdown('<div class="section-head">📉 EXPENSES (Kharch)</div>', unsafe_allow_html=True)
                e1, e2, e3 = st.columns(3)
                sal = e1.number_input("Salary", value=v('salary'), disabled=not can_edit)
                ren = e2.number_input("Rent", value=v('rent'), disabled=not can_edit)
                ele = e3.number_input("Electricity", value=v('electric'), disabled=not can_edit)
                kit = e1.number_input("Kitchen", value=v('kitchen'), disabled=not can_edit)
                tra = e2.number_input("Traveling", value=v('travel'), disabled=not can_edit)
                oth = e3.number_input("Other Expense", value=v('other_exp'), disabled=not can_edit)

                st.markdown('<div class="section-head">💰 INCOME (Aamdani)</div>', unsafe_allow_html=True)
                i1, i2, i3 = st.columns(3)
                gsb = i1.number_input("GSB Income", value=v('gsb'), disabled=not can_edit)
                mab = i2.number_input("MAB Income", value=v('mab'), disabled=not can_edit)
                dpc = i3.number_input("DP Cash", value=v('dp_cash'), disabled=not can_edit)
                dpa = i1.number_input("DP Ashiya", value=v('dp_ashiya'), disabled=not can_edit)
                stc_in = i2.number_input("Staff Cash", value=v('staff_cash'), disabled=not can_edit)
                sta = i3.number_input("Staff Ashiya", value=v('staff_ashiya'), disabled=not can_edit)
                ram = i1.number_input("Ramzan", value=v('ramzan_inc'), disabled=not can_edit)
                tele = i2.number_input("Telethone", value=v('telethone_inc'), disabled=not can_edit)

                if can_edit:
                    if st.form_submit_button("UPDATE CLOUD DATA"):
                        save_data(target, m_key, {
                            "staff_count": sc, "student_count": stc, "salary": sal, "rent": ren,
                            "electric": ele, "kitchen": kit, "travel": tra, "other_exp": oth,
                            "gsb": gsb, "mab": mab, "dp_cash": dpc, "dp_ashiya": dpa,
                            "staff_cash": stc_in, "staff_ashiya": sta, "ramzan_inc": ram, "telethone_inc": tele
                        })
                        st.success("Data Updated!")
                        st.rerun()
                else:
                    st.info("View Only")
                    st.form_submit_button("LOCKED", disabled=True)
        else: st.error("No Access")

    elif st.session_state['tab'] == 'zimmadar':
        if user['role'] in ['zimmadar', 'admin']:
            st.info("Zimmadar Section")
        else: st.error("No Access")

    elif st.session_state['tab'] == 'region':
        if user['role'] == 'admin':
            st.markdown('<div class="section-head">🌎 REGION: MONTHLY & YEARLY PERFORMANCE</div>', unsafe_allow_html=True)

            # 1. Fixed Income Section
            with st.expander("⚙️ Set Fixed Income (Ramzan/Telethone)"):
                col_j, col_r, col_t = st.columns([2,1,1])
                target_j = col_j.selectbox("Select Jamia", j_list, key="reg_sel_j")
                f_data = load_fixed(target_j)
                r_val = col_r.number_input("Ramzan Income", value=float(f_data.get('ramzan', 0)))
                t_val = col_t.number_input("Telethone Income", value=float(f_data.get('telethon', 0)))
                if st.button("Save Fixed Income"):
                    db.collection("fixed_assets").document(target_j).set({"ramzan": r_val, "telethon": t_val})
                    st.success("Saved!")
                    st.rerun()

            # 2. Monthly Calculation
            reg_m = []
            for j in j_list:
                fix = load_fixed(j)
                md = load_data(j, m_key)
                gv, mv = float(md.get('gsb', 0)), float(md.get('mab', 0))
                cv = float(md.get('dp_cash', 0)) + float(md.get('staff_cash', 0))
                av = float(md.get('dp_ashiya', 0)) + float(md.get('staff_ashiya', 0))
                ti = gv + mv + cv + av + fix['ramzan'] + fix['telethon']
                s, r, e = float(md.get('salary', 0)), float(md.get('rent', 0)), float(md.get('electric', 0))
                k, t, o = float(md.get('kitchen', 0)), float(md.get('travel', 0)), float(md.get('other_exp', 0))
                te = s + r + e + k + t + o
                cp = (ti/te*100) if te > 0 else 0
                reg_m.append({"J": j, "G": gv, "M": mv, "C": cv, "A": av, "S": s, "R": r, "E": e, "K": k, "T": t, "O": o, "TI": ti, "TE": te, "D": ti-te, "CP": cp})

            if reg_m:
                df = pd.DataFrame(reg_m)
                sm = df.select_dtypes(include=['number']).sum()
                
                # --- MONTHLY TABLE DISPLAY ---
                html_code = """<style>.myt { width:100%; border-collapse: collapse; text-align: center; font-size: 12px; } .myt th, .myt td { border: 1px solid black; padding: 4px; } .bg-g { background-color: #D3D3D3; font-weight: bold; } .bg-v { background-color: #8A2BE2; color: white; font-weight: bold; } .bg-gr { background-color: #2E8B57; color: white; font-weight: bold; } .t-rd { color: red; font-weight: bold; animation: bk 1s linear infinite; } @keyframes bk { 50% { opacity: 0; } }</style>"""
                html_code += """<table class="myt"><thead><tr><th rowspan="2">Jamia</th><th colspan="4" class="bg-g">INCOME</th><th colspan="6" class="bg-v">EXPENSES</th><th colspan="4" class="bg-gr">SUMMARY</th></tr><tr style="background:#eee;"><th>GSB</th><th>MAB</th><th>Cash</th><th>Ashiya</th><th>Sal</th><th>Rent</th><th>Elec</th><th>Kit</th><th>Tra</th><th>Oth</th><th>T.Inc</th><th>T.Exp</th><th>Deficit</th><th>Cover%</th></tr></thead><tbody>"""
                for _, row in df.iterrows():
                    p = row['CP']
                    cl = "color:green;" if p >= 75 else ("color:blue;" if p >= 59 else "class='t-rd'")
                    html_code += f"<tr><td>{row['J']}</td><td>{row['G']:.0f}</td><td>{row['M']:.0f}</td><td>{row['C']:.0f}</td><td>{row['A']:.0f}</td><td>{row['S']:.0f}</td><td>{row['R']:.0f}</td><td>{row['E']:.0f}</td><td>{row['K']:.0f}</td><td>{row['T']:.0f}</td><td>{row['O']:.0f}</td><td>{row['TI']:.0f}</td><td>{row['TE']:.0f}</td><td>{row['D']:.0f}</td><td {cl}>{p:.1f}%</td></tr>"
                st.markdown(html_code + "</tbody></table>", unsafe_allow_html=True)

                # --- YEARLY SECTION (CORRECTED) ---
                st.markdown("---")
                st.markdown('<div class="section-head">📅 YEARLY REGION BOX REPORT (JAN-DEC)</div>', unsafe_allow_html=True)
                
                months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
                y_html = """<table class="myt" style="margin-top:10px;"><thead style="background:#f4f4f4;"><tr><th>Month</th><th class="bg-g">YEARLY INCOME</th><th class="bg-v">YEARLY EXPENSE</th><th colspan="2" class="bg-gr">YEARLY SUMMARY</th></tr></thead><tbody>"""
                
                for m_name in months:
                    m_inc, m_exp = 0, 0
                    for j in j_list:
                        d = load_data(j, f"{m_name}_2025")
                        f = load_fixed(j)
                        m_inc += float(d.get('gsb',0)) + float(d.get('mab',0)) + float(d.get('dp_cash',0)) + float(d.get('staff_cash',0)) + float(d.get('dp_ashiya',0)) + float(d.get('staff_ashiya',0)) + f['ramzan'] + f['telethon']
                        m_exp += sum([float(d.get(k,0)) for k in ['salary','rent','electric','kitchen','travel','other_exp']])
                    
                    p = (m_inc/m_exp*100) if m_exp > 0 else 0
                    cl = "color:green;" if p >= 75 else ("color:blue;" if p >= 59 else "class='t-rd'")
                    y_html += f"<tr><td>{m_name}</td><td>{m_inc:.0f}</td><td>{m_exp:.0f}</td><td>{m_inc-m_exp:.0f}</td><td {cl}>{p:.1f}%</td></tr>"
                
                st.markdown(y_html + "</tbody></table>", unsafe_allow_html=True)

                # --- BUTTONS ---
                st.markdown("""<button onclick="window.print()" style="width: 100%; background-color: #d9534f; color: white; border: none; padding: 10px; border-radius: 8px; font-weight: bold; cursor: pointer; margin-top: 15px;">📸 PRINT / SAVE AS PDF</button>""", unsafe_allow_html=True)
                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button("📥 DOWNLOAD EXCEL", data=csv, file_name=f"Report_{m_key}.csv", mime='text/csv', use_container_width=True)

    # --- Logout ---
    st.sidebar.markdown("---")
    if st.sidebar.button("🔓 Logout", use_container_width=True):
        st.session_state.clear()

        st.rerun()
