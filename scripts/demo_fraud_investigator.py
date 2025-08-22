import boto3
import json
from datetime import datetime, timedelta
from decimal import Decimal

class FraudInvestigator:
    def __init__(self):
        self.dynamodb = boto3.resource('dynamodb')
        self.table = self.dynamodb.Table('fraud-alerts')
        
    def query_fraud_data(self, query):
        """Process natural language queries about fraud data"""
        query_lower = query.lower()
        
        if "top" in query_lower and "anomalous" in query_lower:
            return self._get_top_anomalous_transactions(query)
        elif "highest fraud scores" in query_lower or "highest scores" in query_lower:
            return self._get_highest_fraud_scores()
        elif "explain" in query_lower and "transaction" in query_lower:
            return self._explain_transaction_flag(query)
        elif "summary" in query_lower or "metrics" in query_lower:
            return self._get_summary_metrics()
        elif "count" in query_lower:
            return self._get_anomaly_count()
        else:
            return self._general_fraud_overview()
    
    def _get_top_anomalous_transactions(self, query):
        """Get top N anomalous transactions"""
        words = query.split()
        limit = 5  # default
        for word in words:
            if word.isdigit():
                limit = int(word)
                break
        
        response = self.table.scan()
        items = response['Items']
        
        sorted_items = sorted(items, key=lambda x: float(x['anomaly_score']), reverse=True)
        top_items = sorted_items[:limit]
        
        result = f"Here are the top {len(top_items)} most anomalous transactions:\n\n"
        
        for i, item in enumerate(top_items, 1):
            result += f"{i}. Transaction {item['transaction_id']}\n"
            result += f"   Customer: {item['customer_id']}\n"
            result += f"   Amount: ${float(item['amount']):,.2f}\n"
            result += f"   Risk Score: {float(item['anomaly_score']):.1f}\n"
            result += f"   Time: {item['timestamp']}\n\n"
        
        return result
    
    def _get_highest_fraud_scores(self):
        """Get customers with highest fraud scores"""
        response = self.table.scan()
        items = response['Items']
        
        customer_scores = {}
        for item in items:
            customer = item['customer_id']
            score = float(item['anomaly_score'])
            if customer not in customer_scores or score > customer_scores[customer]['score']:
                customer_scores[customer] = {
                    'score': score,
                    'transaction_id': item['transaction_id'],
                    'amount': float(item['amount'])
                }
        
        sorted_customers = sorted(customer_scores.items(), key=lambda x: x[1]['score'], reverse=True)
        
        result = "Customers with the highest fraud scores:\n\n"
        for i, (customer, data) in enumerate(sorted_customers[:5], 1):
            result += f"{i}. Customer {customer}\n"
            result += f"   Highest Risk Score: {data['score']:.1f}\n"
            result += f"   Transaction: {data['transaction_id']}\n"
            result += f"   Amount: ${data['amount']:,.2f}\n\n"
        
        return result
    
    def _explain_transaction_flag(self, query):
        """Explain why a transaction was flagged"""
        words = query.split()
        transaction_id = None
        for word in words:
            if word.startswith('TXN'):
                transaction_id = word
                break
        
        if not transaction_id:
            return "Please specify a transaction ID (e.g., TXN999001) to explain why it was flagged."
        
        try:
            response = self.table.get_item(Key={'transaction_id': transaction_id})
            if 'Item' not in response:
                return f"Transaction {transaction_id} not found in fraud alerts."
            
            item = response['Item']
            score = float(item['anomaly_score'])
            amount = float(item['amount'])
            
            explanation = f"Transaction {transaction_id} was flagged as suspicious because:\n\n"
            explanation += f"• Anomaly Score: {score:.1f} (threshold: >2.5)\n"
            explanation += f"• Transaction Amount: ${amount:,.2f}\n"
            explanation += f"• Customer: {item['customer_id']}\n"
            explanation += f"• Transaction Time: {item['timestamp']}\n\n"
            
            if score > 5.0:
                explanation += "CRITICAL RISK: Extremely high anomaly score indicates highly unusual transaction pattern.\n"
            elif score > 4.0:
                explanation += "HIGH RISK: Significantly abnormal transaction behavior detected.\n"
            elif score > 3.0:
                explanation += "MODERATE RISK: Transaction shows suspicious characteristics.\n"
            
            if amount > 30000:
                explanation += "Large transaction amount increases fraud risk.\n"
            
            timestamp = item['timestamp']
            if '02:' in timestamp or '03:' in timestamp or '23:' in timestamp:
                explanation += "Unusual transaction time (late night/early morning).\n"
            
            return explanation
            
        except Exception as e:
            return f"Error retrieving transaction details: {str(e)}"
    
    def _get_summary_metrics(self):
        """Get summary metrics of fraud alerts"""
        response = self.table.scan()
        items = response['Items']
        
        if not items:
            return "No fraud alerts found in the system."
        
        total_alerts = len(items)
        amounts = [float(item['amount']) for item in items]
        scores = [float(item['anomaly_score']) for item in items]
        
        total_amount = sum(amounts)
        avg_amount = total_amount / len(amounts)
        avg_score = sum(scores) / len(scores)
        max_score = max(scores)
        
        customers = set(item['customer_id'] for item in items)
        
        result = "FRAUD DETECTION SUMMARY METRICS\n"
        result += "=" * 40 + "\n\n"
        result += f"Total Fraud Alerts: {total_alerts}\n"
        result += f"Unique Customers Affected: {len(customers)}\n"
        result += f"Total Amount at Risk: ${total_amount:,.2f}\n"
        result += f"Average Transaction: ${avg_amount:,.2f}\n"
        result += f"Average Risk Score: {avg_score:.1f}\n"
        result += f"Highest Risk Score: {max_score:.1f}\n\n"
        
        critical = sum(1 for s in scores if s > 5.0)
        high = sum(1 for s in scores if 4.0 < s <= 5.0)
        moderate = sum(1 for s in scores if 2.5 < s <= 4.0)
        
        result += "RISK DISTRIBUTION:\n"
        result += f"Critical (>5.0): {critical} alerts\n"
        result += f"High (4.0-5.0): {high} alerts\n"
        result += f"Moderate (2.5-4.0): {moderate} alerts\n"
        
        return result

def demo_queries():
    investigator = FraudInvestigator()
    
    print("FraudInvestigator AI Assistant Demo")
    print("=" * 50)
    
    # Demo queries
    queries = [
        "Show me the top 2 anomalous transactions today",
        "List customers with the highest fraud scores this week", 
        "Explain why transaction TXN999004 was flagged as suspicious",
        "Give me a summary of fraud metrics"
    ]
    
    for query in queries:
        print(f"\nQuery: {query}")
        print("-" * 30)
        response = investigator.query_fraud_data(query)
        print(response)
        print()

if __name__ == "__main__":
    demo_queries()