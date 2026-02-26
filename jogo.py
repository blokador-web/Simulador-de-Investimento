import streamlit as st
import random
import pandas as pd

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Trader Elite v10 - Simulador Realista", layout="wide")

# 1. ESTADO DA SESSÃO (BANCO DE DADOS DO JOGO)
def inicializar_estado():
    st.session_state.saldo = 10000.0
    st.session_state.acoes = ["AAPL", "NVDA", "TSLA", "BYD", "PETR4", "VALE3", "MGLU3", "ABEV3", "NFLX", "AMZN", "GOOGL", "META"]
    st.session_state.outros = ["BITCOIN", "DÓLAR", "EURO", "OURO (1g)"]
    st.session_state.renda_fixa = ["TESOURO SELIC", "POUPANÇA"]
    
    # Preços iniciais ajustados para escala legível
    st.session_state.precos = {
        "AAPL": 150.0, "NVDA": 120.0, "TSLA": 90.0, "BYD": 45.0, "PETR4": 35.0, 
        "VALE3": 65.0, "MGLU3": 3.0, "ABEV3": 12.0, "NFLX": 110.0, "AMZN": 85.0, 
        "GOOGL": 70.0, "META": 95.0, "BITCOIN": 350000.0, "DÓLAR": 5.10, "EURO": 5.50, "OURO (1g)": 380.0
    }
    
    ativos_total = st.session_state.acoes + st.session_state.outros + st.session_state.renda_fixa
    st.session_state.carteira = {k: 0.0 for k in ativos_total}
    st.session_state.precos_medios = {k: 0.0 for k in ativos_total}
    st.session_state.precos_antigos = st.session_state.precos.copy()
    st.session_state.historico = {k: [v] for k, v in st.session_state.precos.items()}
    st.session_state.noticia = "Mercado Aberto! Tesouro Selic (13% a.a.) vs Poupança (0.5% a.m.)"
    st.session_state.rodando = False
    st.session_state.ticker_selecionado = "AAPL"
    st.session_state.contador_ciclos = 0

if 'saldo' not in st.session_state: 
    inicializar_estado()

# 2. MOTOR DO MERCADO (OSCILAÇÃO E JUROS)
def atualizar():
    if st.session_state.rodando:
        st.session_state.precos_antigos = st.session_state.precos.copy()
        st.session_state.contador_ciclos += 1
        
        # --- LÓGICA DE RENDA FIXA (A CADA 12 CICLOS / 1 MÊS NO JOGO) ---
        if st.session_state.contador_ciclos >= 12:
            # Poupança: 0.5% fixo por ciclo (Ex: R$ 1000 -> R$ 1005)
            st.session_state.carteira["POUPANÇA"] *= 1.005 
            
            # Tesouro Selic: ~1.02% por ciclo para bater 13% a.a. (Ex: R$ 1000 -> R$ 1010.20)
            # O Tesouro agora rende o dobro da poupança, como na vida real!
            st.session_state.carteira["TESOURO SELIC"] *= 1.0102
            
            st.session_state.noticia = "💰 DIA DE RENDIMENTO! O Tesouro Selic rendeu 1.02% e a Poupança 0.5%."
            st.session_state.contador_ciclos = 0
        
        # --- OSCILAÇÃO DAS AÇÕES E MOEDAS (A cada 2 segundos) ---
        for a in st.session_state.precos:
            # Ativos como Bitcoin e Nvidia oscilam mais (risco maior)
            volatilidade = 0.025 if a in ["BITCOIN", "NVDA", "MGLU3"] else 0.015
            osc = random.uniform(-volatilidade, volatilidade)
            st.session_state.precos[a] *= (1 + osc)
            
            # Salva histórico para o gráfico
            st.session_state.historico[a].append(st.session_state.precos[a])
            st.session_state.historico[a] = st.session_state.historico[a][-30:]

# 3. INTERFACE DO USUÁRIO
@st.fragment(run_every=2)
def renderizar_jogo():
    atualizar()
    
    # --- CABEÇALHO: FINANCEIRO E GRÁFICO ---
    col_fin, col_graf = st.columns([1, 2.5])
    
    with col_fin:
        st.subheader("🏦 Minha Conta")
        st.metric("Saldo em Dinheiro", f"R$ {st.session_state.saldo:,.2f}")
        
        # Cálculo de Patrimônio (Ações + Moedas + Valor depositado na Renda Fixa)
        v_variavel = sum(st.session_state.carteira[a] * st.session_state.precos[a] for a in (st.session_state.acoes + st.session_state.outros))
        v_fixa = st.session_state.carteira["TESOURO SELIC"] + st.session_state.carteira["POUPANÇA"]
        st.metric("Patrimônio Total", f"R$ {(st.session_state.saldo + v_variavel + v_fixa):,.2f}")
        
        c1, c2, c3 = st.columns(3)
        if c1.button("▶️"): st.session_state.rodando = True; st.rerun()
        if c2.button("⏸️"): st.session_state.rodando = False; st.rerun()
        if c3.button("🔄"): inicializar_estado(); st.rerun()
        
        # Barra de Ciclo de Rendimento
        st.write(f"Próximo Juros (Ciclo {st.session_state.contador_ciclos}/12):")
        st.progress(st.session_state.contador_ciclos / 12)

    with col_graf:
        st.subheader(f"📊 Monitor Individual: {st.session_state.ticker_selecionado}")
        st.info(f"📢 {st.session_state.noticia}")
        
        if st.session_state.ticker_selecionado in st.session_state.precos:
            df_hist = pd.DataFrame(st.session_state.historico)
            st.line_chart(df_hist[st.session_state.ticker_selecionado], height=200, color="#00FFAA")
        else:
            st.warning("Renda Fixa não oscila em gráfico, ela cresce em saltos a cada 12 ciclos.")

    # --- MONITOR DE COTAÇÕES (TODAS AS AÇÕES) ---
    st.divider()
    grid = [st.session_state.acoes[i:i+6] for i in range(0, 12, 6)]
    for linha in grid:
        cols = st.columns(6)
        for i, t in enumerate(linha):
            p, ant = st.session_state.precos[t], st.session_state.precos_antigos[t]
            cols[i].metric(t, f"{p:.2f}", f"{p-ant:.2f}")

    st.divider()

    # --- ÁREA DE NEGOCIAÇÃO E CARTEIRA ---
    col_op, col_cart = st.columns([1.2, 2.3])
    
    with col_op:
        st.subheader("🛒 Operar Ativos")
        # Lista para o gráfico e operação
        lista_completa = st.session_state.acoes + st.session_state.outros
        st.session_state.ticker_selecionado = st.selectbox("Selecione para Comprar/Vender", lista_completa)
        
        qtd = st.number_input("Quantidade / Gramas", min_value=0.0, step=1.0)
        p_un = st.session_state.precos[st.session_state.ticker_selecionado]
        st.write(f"Preço Atual: **R$ {p_un:,.2f}**")
        
        b_c, b_v = st.columns(2)
        if b_c.button("COMPRAR", use_container_width=True, type="primary"):
            custo = qtd * p_un * 1.001 # Taxa de 0.1%
            if st.session_state.saldo >= custo and qtd > 0:
                pm_at = st.session_state.carteira[st.session_state.ticker_selecionado] * st.session_state.precos_medios[st.session_state.ticker_selecionado]
                st.session_state.carteira[st.session_state.ticker_selecionado] += qtd
                st.session_state.precos_medios[st.session_state.ticker_selecionado] = (pm_at + (qtd * p_un)) / st.session_state.carteira[st.session_state.ticker_selecionado]
                st.session_state.saldo -= custo
                st.rerun()
        
        if b_v.button("VENDER", use_container_width=True):
            if st.session_state.carteira[st.session_state.ticker_selecionado] >= qtd and qtd > 0:
                st.session_state.saldo += (qtd * p_un) * 0.999
                st.session_state.carteira[st.session_state.ticker_selecionado] -= qtd
                if st.session_state.carteira[st.session_state.ticker_selecionado] == 0:
                    st.session_state.precos_medios[st.session_state.ticker_selecionado] = 0
                st.rerun()

    with col_cart:
        st.subheader("💼 Minha Carteira Global")
        dados_carteira = []
        # Adiciona Ações, Moedas e Ouro
        for a in (st.session_state.acoes + st.session_state.outros):
            q = st.session_state.carteira[a]
            if q > 0:
                pm, pa = st.session_state.precos_medios[a], st.session_state.precos[a]
                lucro = (pa - pm) * q
                dados_carteira.append({"Ativo": a, "Qtd": f"{q:.2f}", "P. Médio": f"{pm:.2f}", "Atual": f"{pa:.2f}", "Lucro R$": f"{lucro:.2f}"})
        
        # Adiciona Renda Fixa
        for f in st.session_state.renda_fixa:
            v = st.session_state.carteira[f]
            if v > 0:
                dados_carteira.append({"Ativo": f, "Qtd": "-", "P. Médio": "-", "Atual": f"R$ {v:.2f}", "Lucro R$": "Rendendo..."})
        
        if dados_carteira:
            st.dataframe(pd.DataFrame(dados_carteira), use_container_width=True, hide_index=True)
        else:
            st.info("Você ainda não possui investimentos.")

    # --- SEÇÃO EXCLUSIVA DE RENDA FIXA ---
    st.divider()
    st.subheader("🏦 Depósitos em Renda Fixa")
    for rf in st.session_state.renda_fixa:
        c_n, c_t, c_s, c_val, c_btns = st.columns([1, 1, 1, 1, 1.5])
        taxa_txt = "13% a.a." if "TESOURO" in rf else "0.5% a.m."
        
        c_n.write(f"**{rf}**")
        c_t.info(taxa_txt)
        c_s.write(f"Saldo: R$ {st.session_state.carteira[rf]:,.2f}")
        
        valor_f = c_val.number_input("Valor", min_value=0.0, step=100.0, key=f"inp_{rf}", label_visibility="collapsed")
        b_dep, b_res = c_btns.columns(2)
        
        if b_dep.button("Depositar", key=f"d_{rf}", use_container_width=True):
            if st.session_state.saldo >= valor_f and valor_f > 0:
                st.session_state.carteira[rf] += valor_f
                st.session_state.saldo -= valor_f
                st.rerun()
        
        if b_res.button("Resgatar", key=f"r_{rf}", use_container_width=True):
            if st.session_state.carteira[rf] >= valor_f and valor_f > 0:
                st.session_state.saldo += valor_f
                st.session_state.carteira[rf] -= valor_f
                st.rerun()

renderizar_jogo()
