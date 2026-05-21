# 🏭 Orçamento Industrial Unificado

Aplicativo interativo em Python utilizando **Streamlit** para cálculo unificado de custos, análise geométrica de arquivos DXF, arranjo de nesting para corte laser, dobra, solda, montagem e geração de propostas comerciais em PDF profissional de 2 páginas.

---

## 🚀 Funcionalidades

1. **📥 Entrada Inteligente de Peças**:
   - **Upload de DXF**: Extração automática das dimensões da peça, perímetro e furos (entradas de corte) utilizando `ezdxf`.
   - **Fórmula de Paridade Industrial**: Estimativa automatizada de tempo de corte laser e peso de material baseado na espessura, perímetro e material.
   - **Aba Manual**: Cadastro manual rápido para itens sem arquivo DXF de forma ágil.
   
2. **📝 Tabela Editável Inteligente**:
   - Tabela interativa para editar quantidades, override de tempos e processos (corte, dobra, solda, etc.) em tempo real, recalculando o lote instantaneamente.

3. **📊 Paridade de Custos & Cascade de Impostos**:
   - Cálculo rigoroso de preços considerando o custo da matéria-prima com IPI embutido, margem de lucro, comissões e impostos em cascata (ICMS, PIS, COFINS, CSLL, IRPJ).

4. **🧩 Nesting de Chapas**:
   - Simulação e visualização gráfica (`matplotlib`) do arranjo e rendimento das peças nas chapas padrão da empresa (1200x2400mm ou customizado).

5. **📄 Emissão e Customização de PDF Comercial (2 Páginas)**:
   - **Personalização completa na interface**: Upload persistente de logotipo e edição dinâmica dos dados da empresa e das 7 condições gerais de fornecimento.
   - **Página 1**: Cabeçalho corporativo, dados do cliente/vendedor, tabela detalhada com miniaturas geométricas reais dos itens, totais de peso/valor e observações.
   - **Página 2**: Termos comerciais e "Condições Gerais de Fornecimento".

---

## 🛠️ Instalação e Execução

### Pré-requisitos
Certifique-se de ter o Python 3.9+ instalado em sua máquina.

### Executando Localmente (Windows)
Basta dar dois cliques no arquivo:
```bash
iniciar.bat
```
*(O script instalará as dependências do `requirements.txt` na primeira execução e abrirá o navegador automaticamente no endereço local do Streamlit).*

### Executando Manualmente
1. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```
2. Execute o Streamlit:
   ```bash
   streamlit run app.py
   ```

---

## 📁 Estrutura de Arquivos Recomendada para Git

- `app.py`: Interface gráfica e lógica principal.
- `calculos.py`: Fórmulas de reversão e paridade comercial da planilha original.
- `dxf_utils.py`: Processamento geométrico dos arquivos DXF.
- `estilos.py`: Folha de estilo visual customizada (Tema Light Moderno).
- `gerador_pdf.py`: Engine de renderização de PDF profissional usando ReportLab.
- `requirements.txt`: Dependências do Python.
- `iniciar.bat`: Script de inicialização rápida.
- `.gitignore`: Arquivo para evitar subir arquivos locais de cache ou confidenciais.

---

*Desenvolvido para otimizar o fluxo comercial e agilizar orçamentos industriais de corte e dobra.*
