

Pull Invoices --- No PO invoices 

-----------------------------------------------
1000 Invoices -::Script to classify invoices::-
-----------------------------------------------
- If not attachment - do not pull this -- 
- Classification API 
- 

Invoices - 

1. Invoice Date is the only piece of information - and $ amount

2. Invoice Data and $ amount 
and Charge Date on separate days

3. Billing Statement - Statement Date = Invoice Date
Statement Period is what we want to go off 
-----
------

Template 1	
	{
	"invoice_id":122334
	"invoice_date":""
	"invoice_amount":""
	}
	
Template 2

{
	"invoice_id":122334
	"invoice_date":
	"invoice_amount"
	"charge_dates":["","",....]
	}

Template 3	
{
	"invoice_id":122334
	"statement_date":
	"invoice_amount"
	"statement_period":{"Start_date":"", "End_date":""
		}
	}






CXML -Nothing to Review