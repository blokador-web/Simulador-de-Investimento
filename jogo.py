import streamlit as st
import random
import pandas as pd

# --- CONFIGURAÇÕES DE TAXAS ---
TAXA_CORRETAGEM = 0.001  # 0.1%
TAXA_IR = 0.007          # 0.7%

# 1. Configuração de Página
st.set_page_config(page_title="Simulador Elite: PRO", layout="wide")

# 2. Estado da Sessão
def inicializar_estado():
    st.session_state.saldo = 10000.0
    st.session_state.carteira = {"PETR": 0, "VALE": 0, "TECH": 0, "BANK": 0}
    st.session_state.precos_compra = {"PETR": 0.0, "VALE": 0.0, "TECH": 0.0, "BANK": 0.0}
    st.session_state.precos = {"PETR": 25.0, "VALE": 70.0, "TECH": 15.0, "BANK": 35.0}
    st.session_state.precos_base = st.session_state.precos.copy()
    st.session_state.precos_antigos = st.session_state.precos.copy()
    st.session_state.historico = {k: [v] for k, v in st.session_state.precos.items()}
    st.session_state.pressao = {"PETR": 0.0, "VALE": 0.0, "TECH": 0.0, "BANK": 0.0}
    st.session_state.logs_bots = []
    st.session_state.noticia = "Aguardando abertura do pregão..."
    st.session_state.rodando = False

if 'saldo' not in st.session_state:
    inicializar_estado()

# --- CABEÇALHO ---
status_cor = "#2ecc71" if st.session_state.rodando else "#e74c3c"
st.markdown(f"<h1>Simulador Elite <span style='font-size: 14px; color: {status_cor};'>● {'ON' if st.session_state.rodando else 'OFF'}</span></h1>", unsafe_allow_html=True)

# 3. MOTOR DE EVENTOS REAIS (Fatores Fundamentais)
def processar_evento():
    eventos_bons = [
        ("PETR", 1.07, "🛢️ PETR: Descoberta de novo poço no pré-sal impulsiona ativos!"),
        ("TECH", 1.10, "💻 TECH: Empresa adquire startup de IA revolucionária!"),
        ("VALE", 1.06, "⛏️ VALE: Preço do minério de ferro sobe na China."),
        ("BANK", 1.05, "🏦 BANK: Lucro trimestral bate recorde histórico!"),
        ("TECH", 1.08, "🚀 TECH: Lançamento de novo processador esgota em minutos.")
    ]
    eventos_ruins = [
        ("PETR", 0.93, "📉 PETR: Queda no preço do barril de petróleo afeta margens."),
        ("BANK", 0.94, "🏦 BANK: Aumento da inadimplência preocupa investidores."),
        ("VALE", 0.90, "⚠️ VALE: Interdição judicial em mina reduz produção anual."),
        ("TECH", 0.92, "🛑 TECH: Falha crítica de segurança em massa derruba sistemas."),
        ("PETR", 0.95, "⛽ PETR: Governo anuncia mudança na política de dividendos.")
    ]
    
    if random.random() < 0.05:
        tipo = random.choice(["bom", "ruim"])
        ativo, impacto, msg = random.choice(eventos_bons if tipo == "bom" else eventos_ruins)
        st.session_state.precos[ativo] *= impacto
        st.session_state.noticia = msg

# 4. Lógica de Mercado Principal
@st.fragment(run_every=2)
def renderizar_painel():
    if st.session_state.rodando:
        st.session_state.precos_antigos = st.session_state.precos.copy()
        processar_evento()
        
        for acao in st.session_state.precos:
            oscilacao = random.uniform(-0.03, 0.03)
            mov_bots = random.choice([-0.02, 0.02]) if random.random() < 0.3 else 0
            recup = (st.session_state.precos_base[acao] - st.session_state.precos[acao]) * 0.005
            
            st.session_state.precos[acao] += oscilacao + mov_bots + recup
            st.session_state.historico[acao].append(st.session_state.precos[acao])
            st.session_state.historico[acao] = st.session_state.historico[acao][-30:]

    # --- LAYOUT ---
    st.info(f"📢 **FATO RELEVANTE:** {st.session_state.noticia}")
    c_painel, c_grafico, c_operar = st.columns([1, 1.5, 1])

    with c_painel:
        st.subheader("🕹️ Controles")
        btn1, btn2, btn3 = st.columns(3)
        with btn1:
            if st.button("▶️", use_container_width=True): st.session_state.rodando = True; st.rerun()
        with btn2:
            if st.button("⏸️", use_container_width=True): st.session_state.rodando = False; st.rerun()
        with btn3:
            if st.button("🔄", use_container_width=True): inicializar_estado(); st.rerun()
                
        st.write("---")
        st.subheader("💼 Carteira")
        v_acoes = sum(st.session_state.carteira[a] * st.session_state.precos[a] for a in st.session_state.carteira)
        patrimonio = st.session_state.saldo + v_acoes
        st.metric("Patrimônio Total", f"R$ {patrimonio:.2f}", delta=f"{patrimonio - 10000:.2f}")
        st.metric("Saldo em Conta", f"R$ {st.session_state.saldo:.2f}")
        
        for acao, qtd in st.session_state.carteira.items():
            if qtd > 0:
                pago = st.session_state.precos_compra[acao]
                atual = st.session_state.precos[acao]
                v_liq = atual * (1 - (TAXA_CORRETAGEM + TAXA_IR))
                lucro = (v_liq - pago) * qtd
                cor = "green" if lucro > 0 else "red"
                st.markdown(f"**{acao}**: {qtd} un. | Lucro: <span style='color:{cor}'>R$ {lucro:.2f}</span>", unsafe_allow_html=True)

        st.write("---")
        st.markdown(f"""
        <div style="border: 1px solid #444; padding: 10px; border-radius: 5px;">
            <p style="margin:0; font-size: 13px;"><b>Corretagem:</b> {TAXA_CORRETAGEM*100:.1f}% | <b>I.R.:</b> {TAXA_IR*100:.1f}%</p>
        </div>
        """, unsafe_allow_html=True)

    with c_grafico:
        st.subheader("📊 Gráfico em Tempo Real")
        st.line_chart(pd.DataFrame(st.session_state.historico), height=280)
        cols = st.columns(4)
        for i, (acao, preco) in enumerate(st.session_state.precos.items()):
            antigo = st.session_state.precos_antigos.get(acao, preco)
            cols[i].metric(acao, f"{preco:.2f}", f"{preco-antigo:.2f}")

    with c_operar:
        st.subheader("🛒 Boleta de Operação")
        acao_op = st.selectbox("Ativo", list(st.session_state.precos.keys()))
        qtd_op = st.number_input("Quantidade", min_value=0, step=10)
        preco_atual = st.session_state.precos[acao_op]
        
        o1, o2 = st.columns(2)
        with o1:
            if st.button("Comprar", type="primary", use_container_width=True):
                v_bruto = qtd_op * preco_atual
                custo_t = v_bruto * (TAXA_CORRETAGEM + TAXA_IR)
                if st.session_state.saldo >= (v_bruto + custo_t) and qtd_op > 0:
                    q_ant = st.session_state.carteira[acao_op]
                    p_ant = st.session_state.precos_compra[acao_op]
                    n_qtd = q_ant + qtd_op
                    st.session_state.precos_compra[acao_op] = ((q_ant * p_ant) + (v_bruto + custo_t)) / n_qtd
                    st.session_state.saldo -= (v_bruto + custo_t)
                    st.session_state.carteira[acao_op] = n_qtd
                    st.rerun()

        with o2:
            if st.button("Vender", use_container_width=True):
                if st.session_state.carteira[acao_op] >= qtd_op and qtd_op > 0:
                    v_bruto = qtd_op * preco_atual
                    custo_t = v_bruto * (TAXA_CORRETAGEM + TAXA_IR)
                    st.session_state.saldo += (v_bruto - custo_t)
                    st.session_state.carteira[acao_op] -= qtd_op
                    if st.session_state.carteira[acao_op] == 0: st.session_state.precos_compra[acao_op] = 0.0
                    st.rerun()
        
        st.write("---")
        st.subheader("⏳ Últimos Eventos")
        st.caption(st.session_state.noticia)

renderizar_painel()
