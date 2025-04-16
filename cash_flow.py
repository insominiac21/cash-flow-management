import streamlit as st
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt


class CashFlowGraph:
    def __init__(self):
        self.graph = nx.DiGraph() # Initializes an empty Directed graph 
    
    def add_transaction(self, payer, payee, amount):
        if self.graph.has_edge(payer, payee):
            self.graph[payer][payee]['weight'] += amount
        else:
            self.graph.add_edge(payer, payee, weight=amount)

    def optimize_transactions_floyd_warshall(self):
        balance = {}
        for u, v, data in self.graph.edges(data=True):
            amount = data['weight']
            balance[u] = balance.get(u, 0) - amount
            balance[v] = balance.get(v, 0) + amount

        debtors = []
        creditors = []
        for person, amt in balance.items():
            if amt < 0:
                debtors.append((person, -amt))
            elif amt > 0:
                creditors.append((person, amt))

        self.graph = nx.DiGraph() #delare another graph for optimised one
        i, j = 0, 0
        while i < len(debtors) and j < len(creditors):
            debtor, debt_amt = debtors[i] #debtor = i, debt_amt = amount owed
            creditor, credit_amt = creditors[j]
            # direct the highest giver  to highest owed one
            trans_amt = min(debt_amt, credit_amt) 
            self.graph.add_edge(debtor, creditor, weight=trans_amt)
            debt_amt -= trans_amt
            credit_amt -= trans_amt
            if debt_amt == 0: 
                i += 1
            else: #highest debtor still owes money!
                debtors[i] = (debtor, debt_amt) #update the amount owed

            if credit_amt == 0:
                j += 1
            else:
                creditors[j] = (creditor, credit_amt)

    def draw_graph(self, title="Cash Flow Graph"):
        fig, ax = plt.subplots(figsize=(10, 6)) 
        pos = nx.shell_layout(self.graph)
        labels = {
            edge: f"Rs{self.graph[edge[0]][edge[1]]['weight']}" for edge in self.graph.edges
        }
        nx.draw(self.graph, pos, with_labels=True, node_color="lightblue",
                edge_color="gray", node_size=2500, font_size=12,
                font_weight='bold', arrowsize=20, connectionstyle="arc3,rad=0.1")
        nx.draw_networkx_edge_labels(self.graph, pos, edge_labels=labels,
                                     font_color='green', font_size=10)
        ax.set_title(title)
        ax.axis("off")
        st.pyplot(fig)

def main():
    st.title("💸 Cash Flow Optimizer")
    mode = st.sidebar.radio("Choose Mode", ["Manual Input", "Test Cases", "Upload Excel File"])

    if mode == "Manual Input":
        st.subheader("Enter Transactions Manually")
        num_txns = st.number_input("Number of Transactions", min_value=1, step=1)
        txns = [] 
        for i in range(num_txns):
            st.markdown(f"**Transaction {i+1}**")
            payer = st.text_input(f"Payer {i+1}", key=f"payer_{i}")
            payee = st.text_input(f"Payee {i+1}", key=f"payee_{i}")
            amount = st.number_input(f"Amount {i+1}", min_value=1, step=1, key=f"amount_{i}")
            txns.append((payer, payee, amount)) 

        if st.button("Optimize"):
            graph = CashFlowGraph() # Initialize the graph
            for p, q, a in txns:
                if p and q and a:
                    graph.add_transaction(p, q, a)
            st.write("### Original Graph")
            graph.draw_graph("Original Transactions")
            graph.optimize_transactions_floyd_warshall()
            st.write("### Optimized Graph")
            graph.draw_graph("Optimized Transactions")

    elif mode == "Test Cases":
        st.subheader("Running Test Cases")
        test_cases = [
            {
                "name": "Basic Triangle Debt",
                "transactions": [("A", "B", 100), ("B", "C", 100), ("C", "A", 100)]
            },
            {
                "name": "Simple Netting Case",
                "transactions": [("A", "B", 50), ("B", "C", 30), ("A", "C", 20)]
            },
            {
                "name": "Four Person Complex Debt",
                "transactions": [("A", "B", 40), ("A", "C", 30), ("B", "D", 20), ("C", "D", 50)]
            }
        ]

        for case in test_cases:
            st.write(f"### Test Case: {case['name']}")
            graph = CashFlowGraph()
            for p, q, a in case["transactions"]:
                graph.add_transaction(p, q, a)
            st.write("Original Graph:")
            graph.draw_graph(case["name"] + " - Original")
            graph.optimize_transactions_floyd_warshall()
            st.write("Optimized Graph:")
            graph.draw_graph(case["name"] + " - Optimized")

    elif mode == "Upload Excel File":
        st.subheader("Upload Excel with columns: group no., payer, payee, amount")
        uploaded_file = st.file_uploader("Upload your Excel file", type=["xlsx"])
        if uploaded_file:
            df = pd.read_excel(uploaded_file)
            st.success("File uploaded successfully")
            group_ids = sorted(df['group no.'].unique())
            chosen_group = st.selectbox("Select Group Number", group_ids)

            sub_df = df[df['group no.'] == chosen_group]
            original_graph = CashFlowGraph()
            for _, row in sub_df.iterrows():
                original_graph.add_transaction(row['payer'], row['payee'], row['amount'])
            st.write("### Original Transactions")
            original_graph.draw_graph(f"Original Transactions (Group {chosen_group})")

            original_graph.optimize_transactions_floyd_warshall()
            st.write("### Optimized Transactions")
            original_graph.draw_graph(f"Optimized Transactions (Group {chosen_group})")

if __name__ == "__main__":
    main()