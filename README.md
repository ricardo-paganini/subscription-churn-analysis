\# 📉 Análise de Churn de Assinatura: NetVida Telecom



Estudo de caso de análise de dados para entender \*\*por que os clientes de um provedor de internet cancelam\*\* e como a empresa pode agir antes que isso aconteça.



\## Sobre o projeto



A NetVida Telecom é um provedor de internet fictício que perdeu \*\*712 de 3.000 clientes em 2025 (23,7% de churn)\*\*. Neste projeto, usei Python e SQL, seguindo a metodologia \*\*CRISP-DM\*\*, para descobrir quais sinais antecedem o cancelamento e criar um modelo que ajude a equipe de retenção a priorizar os clientes em risco.



\## Perguntas de negócio



1\. Qual é a taxa de churn da empresa?

2\. Quais tipos de contrato, planos e formas de pagamento têm mais cancelamentos?

3\. Chamados de suporte estão ligados ao cancelamento?

4\. Atrasos de pagamento estão ligados ao cancelamento?

5\. É possível prever quais clientes têm mais chance de cancelar?



\## Principais resultados



\- \*\*Chamados de suporte\*\* são o sinal mais forte: a taxa de churn vai de \*\*11,6%\*\* (nenhum chamado) para \*\*73,2%\*\* (4 ou mais).

\- O \*\*contrato mensal\*\* tem \*\*34,3%\*\* de churn, contra 14,8% do anual e 10,7% do bienal.

\- \*\*Atrasos\*\* só preocupam a partir da 3ª fatura: a taxa sobe de 21,7% (2 atrasos) para \*\*37,5%\*\* (3) e \*\*64,6%\*\* (4 ou mais).

\- Um modelo \*\*Random Forest\*\* encontrou \*\*63%\*\* dos clientes que cancelaram. Entre os clientes marcados como risco, 45% realmente cancelaram, quase o dobro da taxa normal.

\- Recomendações: alerta no 2º chamado, desconto para migrar do contrato mensal para o anual, alerta na 3ª fatura atrasada e lista mensal de clientes em risco.



\## Ferramentas



\- Python (pandas, numpy, matplotlib, seaborn, scikit-learn)

\- SQL (SQLite)

\- Jupyter Notebook

\- Git e GitHub



\## Como reproduzir



No Prompt de Comando do Windows:



```bash

git clone https://github.com/ricardo-paganini/subscription-churn-analysis.git

cd subscription-churn-analysis

python -m venv venv

venv\\Scripts\\activate

pip install -r requirements.txt

python -m ipykernel install --user --name=churn-venv --display-name="Python (churn)"

jupyter notebook

```



Abra o arquivo `churn\_analysis.ipynb`, escolha o kernel \*\*Python (churn)\*\* e rode em \*\*Kernel > Restart \& Run All\*\*.



No Linux e no Mac, a ativação do ambiente é `source venv/bin/activate`.



\## Arquivos



| Arquivo | Descrição |

|---|---|

| `churn\_analysis.ipynb` | Notebook com todo o projeto, do entendimento do negócio às recomendações |

| `generate\_data.py` | Script que gera as bases fictícias (com sementes fixas) |

| `customers.csv` | Dados dos clientes |

| `tickets.csv` | Chamados de suporte abertos em 2025 |

| `payments.csv` | Faturas e pagamentos de 2025 |

| `requirements.txt` | Bibliotecas e versões usadas |



\## Observação sobre os dados



Os dados são \*\*fictícios\*\*, gerados por script para este estudo de caso, e foram criados com problemas reais (valores vazios, duplicados e textos escritos de formas diferentes) para mostrar o processo de limpeza.

