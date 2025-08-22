import json
import boto3
import os
from decimal import Decimal

def lambda_handler(event, context):
    """AWS Lambda handler for FraudInvestigator queries"""
    
    # Initialize DynamoDB
    dynamodb = boto3.resource('dynamodb')
    table_name = os.environ['DYNAMODB_TABLE']
    table = dynamodb.Table(table_name)
    
    # Get query from event
    query = event.get('query', '')
    
    try:
        # Process the query
        investigator = FraudInvestigator(table)
        response = investigator.query_fraud_data(query)
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'query': query,
                'response': response
            })
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e)
            })
        }

class FraudInvestigator:
    def __init__(self, table):
        self.table = table
        
    def query_fraud_data(self, query):
        """Process natural language queries about fraud data"""
        query_lower = query.lower()
        
        if "top" in query_lower and ("anomalous" in query_lower or "risky" in query_lower):
            return self._get_top_anomalous_transactions(query)
        elif "highest" in query_lower and "scores" in query_lower:
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
        limit = 5
        for word in words:
            if word.isdigit():
                limit = int(word)
                break
        
        response = self.table.scan()
        items = response['Items']
        
        sorted_items = sorted(items, key=lambda x: float(x['anomaly_score']), reverse=True)
        top_items = sorted_items[:limit]
        
        result = f"Top {len(top_items)} most anomalous transactions:\\n\\n"
        
        for i, item in enumerate(top_items, 1):
            result += f"{i}. {item['transaction_id']} - Score: {float(item['anomaly_score']):.1f} - ${float(item['amount']):,.2f}\\n"
        
        return result
    
    def _get_highest_fraud_scores(self):
        """Get customers with highest fraud scores"""
        response = self.table.scan()
        items = response['Items']
        
        customer_scores = {}
        for item in items:
            customer = item['customer_id']
            score = float(item['anomaly_score'])
            if customer not in customer_scores or score > customer_scores[customer]:
                customer_scores[customer] = score
        
        sorted_customers = sorted(customer_scores.items(), key=lambda x: x[1], reverse=True)
        
        result = "Customers with highest fraud scores:\\n"
        for customer, score in sorted_customers[:5]:
            result += f"• {customer}: {score:.1f}\\n"
        
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
            return "Please specify a transaction ID to explain."
        
        try:
            response = self.table.get_item(Key={'transaction_id': transaction_id})
            if 'Item' not in response:
                return f"Transaction {transaction_id} not found."
            
            item = response['Item']
            score = float(item['anomaly_score'])
            amount = float(item['amount'])
            
            explanation = f"Transaction {transaction_id} flagged because:\\n"
            explanation += f"• Anomaly Score: {score:.1f} (>2.5 threshold)\\n"
            explanation += f"• Amount: ${amount:,.2f}\\n"
            
            if score > 5.0:
                explanation += "• CRITICAL: Extremely unusual pattern\\n"
            elif score > 4.0:
                explanation += "• HIGH RISK: Abnormal behavior\\n"
            
            if amount > 30000:
                explanation += "• Large transaction amount\\n"
            
            return explanation
            
        except Exception as e:
            return f"Error: {str(e)}"
    
    def _get_summary_metrics(self):
        """Get summary metrics"""
        response = self.table.scan()
        items = response['Items']
        
        if not items:
            return "No fraud alerts found."
        
        total_alerts = len(items)
        amounts = [float(item['amount']) for item in items]
        scores = [float(item['anomaly_score']) for item in items]
        
        total_amount = sum(amounts)
        avg_score = sum(scores) / len(scores)
        max_score = max(scores)
        
        result = f"FRAUD SUMMARY:\\n"
        result += f"• Total Alerts: {total_alerts}\\n"
        result += f"• Total at Risk: ${total_amount:,.2f}\\n"
        result += f"• Average Score: {avg_score:.1f}\\n"
        result += f"• Highest Score: {max_score:.1f}\\n"
        
        return result
    
    def _get_anomaly_count(self):
        """Get count of anomalies"""
        response = self.table.scan()
        return f"Current fraud alerts: {len(response['Items'])}"
    
    def _general_fraud_overview(self):
        """General overview"""
        response = self.table.scan()
        items = response['Items']
        
        if not items:
            return "No fraud alerts in system."
        
        sorted_items = sorted(items, key=lambda x: float(x['anomaly_score']), reverse=True)
        top_item = sorted_items[0]
        
        return f"Monitoring {len(items)} fraud alerts. Highest risk: {top_item['transaction_id']} (Score: {float(top_item['anomaly_score']):.1f})"