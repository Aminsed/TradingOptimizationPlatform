 //+------------------------------------------------------------------+
//|                                           Amin MA ATR MT4 EA.mq4 |
//|                                             Abdellahfx@gmail.com |
//|                             https://www.fiverr.com/mehdimehdi501 |
//+------------------------------------------------------------------+
#property copyright "Abdellahfx@gmail.com"
#property link      "https://www.fiverr.com/mehdimehdi501"
#property version   "1.00"
#property strict
#define MAX_PERCENT 100


//+-----------------------------------------------------------------------------------------------------------------+
//| Input variables                                                  
//+-----------------------------------------------------------------------------------------------------------------+


input double   RiskPercent          = 2.0;      //percent_invest
input int      SlowMaPeriod         = 15;       //slow_ma
input int      FastMaPeriod         = 5;        //fast_ma
input int            ATRperiod            =8;        //ATR_window_size
input double   MinProfitPipsTSatr   = 1.5;      //t_sl
input double   ProfitATR            =3.0;       //tp









 double   SlippagePips         = 20.0;      //Slippage (pips)
 int      MagicNumber          = 20221113;  //Magic number      
 bool     UseMoneyManagement   = true;    //Use money management
 double   FixedLotSize         = 0.01;     //Fixed lot size
 double   StopPips             = 0.0;     //Stop loss (pips)
 double   ProfitPips           =0.0;       //Take profit (pips)
 bool     UseTrailingStop      = true;    //Use trailing stop
 double   TrailPips            = 0.0;     //Trailing stop distance (pips)
 double   MinProfitPipsTS      = 0.0;     //Minimum profit (pips)
 double   StepPips             = 1.0;      //Trail step (pips)


double takeprofit;
double stoploss;
double trailingstart;
double trailingstep;
double trailingstop;
double breakstart;
double breakstop;
double slippage;

double lots,SL,TP,sell,buy,close,move;
int ThisBarTrade=0;
bool NewBar;
double minsltp;
bool  IsErrors;






//+------------------------------------------------------------------+
//| Expert initialization function                                   |
//+------------------------------------------------------------------+
int OnInit()
  {
//---

   // Input validation
   IsErrors = false;

   // Money management
   if(fnValidateMoneyManagement(UseMoneyManagement,RiskPercent,FixedLotSize) == false) IsErrors = true;


   // Convert pip inputes to points
   int pipFactor  = fnCalculatePipFactor(_Symbol);
   


slippage=0;

stoploss=0;
takeprofit=0;
breakstart=0;
breakstop=0;
trailingstart=0;
trailingstop=0;
trailingstep=0;

   // Convert pip inputes to points

if(StopPips!=0)stoploss=int(StopPips*pipFactor);
if(ProfitPips!=0)takeprofit=int(ProfitPips*pipFactor);

if(MinProfitPipsTS!=0)trailingstart=int(MinProfitPipsTS*pipFactor);
if(TrailPips!=0)trailingstop=int(TrailPips*pipFactor);
if(StepPips!=0)trailingstep=int(StepPips*pipFactor);
if(SlippagePips!=0)slippage=int(SlippagePips*pipFactor);
//---





   return(INIT_SUCCEEDED);
  }
//+------------------------------------------------------------------+
//| Expert deinitialization function                                 |
//+------------------------------------------------------------------+
void OnDeinit(const int reason)
  {
//---

  }
//+------------------------------------------------------------------+
//| Expert tick function                                             |
//+------------------------------------------------------------------+
void OnTick()
  {
//---
   if(iBars(Symbol(),0)!=ThisBarTrade) 
     {
      NewBar=true;
      ThisBarTrade=iBars(Symbol(),0);
      NewBar=true;
     }
//---
   minsltp=(MarketInfo(Symbol(),MODE_SPREAD)+MarketInfo(Symbol(),MODE_STOPLEVEL)+1);

//---

double fastma1=iMA(Symbol(),0,FastMaPeriod,0,MODE_EMA,PRICE_CLOSE,1);
double slowma1=iMA(Symbol(),0,SlowMaPeriod,0,MODE_EMA,PRICE_CLOSE,1);


double fastma2=iMA(Symbol(),0,FastMaPeriod,0,MODE_EMA,PRICE_CLOSE,2);
double slowma2=iMA(Symbol(),0,SlowMaPeriod,0,MODE_EMA,PRICE_CLOSE,2);





   if(fastma1<slowma1)CloseOrders(OP_BUY);
   if(fastma1>slowma1)CloseOrders(OP_SELL);





   if(NewBar&&fastma1>slowma1&&fastma2<=slowma2&&orderscnt(OP_BUY)==0){

CloseOrders(OP_SELL);

     
     double atr=iATR(Symbol(),0,ATRperiod,1);
     
if(MinProfitPipsTSatr!=0)stoploss=(int)((atr*MinProfitPipsTSatr)/Point);
stoploss=MathMax(stoploss,minsltp);

    
   if(ProfitATR==0){TP=0;}else{TP=Ask+atr*ProfitATR;}
   if(TP!=0)TP=MathMax(TP,Ask+minsltp*Point);
   if(MinProfitPipsTSatr==0){SL=0;}else{SL=Ask-stoploss*Point;}




       lots = FixedLotSize;
      if(UseMoneyManagement == true)
      {
         lots = MoneyManagement(_Symbol,FixedLotSize,RiskPercent,(int)stoploss); 
      }

      if(lots<MarketInfo(Symbol(),MODE_MINLOT))lots=MarketInfo(Symbol(),MODE_MINLOT);
      if(lots>MarketInfo(Symbol(),MODE_MAXLOT))lots=MarketInfo(Symbol(),MODE_MAXLOT);
      buy=OrderSend(Symbol(),OP_BUY,NormalizeDouble(lots,2),Ask,(int)slippage,SL,TP,"Amin MA ATR MT4 EA",MagicNumber,0,clrBlue);
      NewBar=false;
     }




   if(NewBar&&fastma1<slowma1&&fastma2>=slowma2&&orderscnt(OP_SELL)==0){

CloseOrders(OP_BUY);
double atr=iATR(Symbol(),0,ATRperiod,1);


if(MinProfitPipsTSatr!=0)stoploss=(int)((atr*MinProfitPipsTSatr)/Point);
stoploss=MathMax(stoploss,minsltp);
      
      if(ProfitATR==0){TP=0;}else{TP=Bid-atr*ProfitATR;}
      if(TP!=0)TP=MathMin(TP,Bid-minsltp*Point);
      if(MinProfitPipsTSatr==0){SL=0;}else{SL=Bid+stoploss*Point;}


       lots = FixedLotSize;
      if(UseMoneyManagement == true)
      {
         lots = MoneyManagement(_Symbol,FixedLotSize,RiskPercent,(int)stoploss); 
      }

      if(lots<MarketInfo(Symbol(),MODE_MINLOT))lots=MarketInfo(Symbol(),MODE_MINLOT);
      if(lots>MarketInfo(Symbol(),MODE_MAXLOT))lots=MarketInfo(Symbol(),MODE_MAXLOT);
      sell=OrderSend(Symbol(),OP_SELL,NormalizeDouble(lots,2),Bid,(int)slippage,SL,TP,"Amin MA ATR MT4 EA",MagicNumber,0,clrRed);
      NewBar=false;
     }
     
     
     if(UseTrailingStop)DoTrail();
    

  }
//+------------------------------------------------------------------+
   int orderscnt(int tip)
     {
      int cnt=0;
      for(int i=0;i<OrdersTotal();i++)
        {
         if (OrderSelect(i, SELECT_BY_POS, MODE_TRADES))
         if(OrderSymbol()==Symbol() &&OrderType()==tip&&OrderMagicNumber()==MagicNumber)
           {
            cnt++;
           }
        }
      return(cnt);
     }
//***************************//
   int orderstotal()
     {
      int cnt=0;
      for(int i=0;i<OrdersTotal();i++)
        {
         if (OrderSelect(i, SELECT_BY_POS, MODE_TRADES))
         if(OrderSymbol()==Symbol() &&OrderMagicNumber()==MagicNumber)
           {
            cnt++;
           }
        }
      return(cnt);
     }
//***************************//

void DoTrail()
  {
   for(int i=0;i<OrdersTotal();i++)
     {
      if(OrderSelect(i,SELECT_BY_POS,MODE_TRADES))
      
      //Check order if it matches current chart symbol and our magic number
         if(OrderMagicNumber()==MagicNumber && OrderSymbol()==Symbol())
           {
           
           int shift=iBarShift(Symbol(),0,OrderOpenTime(),false);
double atr=iATR(Symbol(),0,ATRperiod,shift);

trailingstart=(atr*MinProfitPipsTSatr)/Point;
trailingstop=(atr*MinProfitPipsTSatr)/Point;
trailingstep=(atr*MinProfitPipsTSatr)/Point;


            //========TO TRAIL SL THE FIRST TIME
            if(trailingstart!=0&&OrderType()==OP_BUY && (OrderStopLoss()<OrderOpenPrice() || OrderStopLoss()==0) && 
               OrderClosePrice()-OrderOpenPrice()>trailingstart*Point)
              {

             if(trailingstop!=0)  SL=OrderClosePrice()-trailingstop*Point;

if(NormalizeDouble(SL,Digits)>NormalizeDouble(OrderStopLoss(),Digits)){
move=OrderModify(OrderTicket(),OrderOpenPrice(),SL,OrderTakeProfit(),0,clrBlue);}

              }


            if(trailingstart!=0&&OrderType()==OP_SELL && (OrderStopLoss()>OrderOpenPrice() || OrderStopLoss()==0) && 
               OrderOpenPrice()-OrderClosePrice()>trailingstart*Point)
              {

             if(trailingstop!=0)  SL=OrderClosePrice()+trailingstop*Point;

if(NormalizeDouble(SL,Digits)<NormalizeDouble(OrderStopLoss(),Digits)||OrderStopLoss()==0){
move=OrderModify(OrderTicket(),OrderOpenPrice(),SL,OrderTakeProfit(),0,clrBlue);}

              }
              //==========================================
              
              
              
              //======NOW TO TRAIL SL THE FOLLOWING TIMES
             if((trailingstop+trailingstep)!=0&&OrderType()==OP_BUY &&OrderStopLoss()!=0&&OrderStopLoss()>=OrderOpenPrice()&&
             OrderClosePrice()-OrderStopLoss()>(trailingstop+trailingstep)*Point)
              {

             if(trailingstop!=0)  SL=OrderClosePrice()-trailingstop*Point;

if(NormalizeDouble(SL,Digits)>NormalizeDouble(OrderStopLoss(),Digits)){
 move=OrderModify(OrderTicket(),OrderOpenPrice(),SL,OrderTakeProfit(),0,clrBlue);}

              }


            if((trailingstop+trailingstep)!=0&&OrderType()==OP_SELL &&OrderStopLoss()!=0&&OrderStopLoss()<=OrderOpenPrice()&&
            OrderStopLoss()-OrderClosePrice()>(trailingstop+trailingstep)*Point)
              {

              if(trailingstop!=0) SL=OrderClosePrice()+trailingstop*Point;

if(NormalizeDouble(SL,Digits)<NormalizeDouble(OrderStopLoss(),Digits)){
move=OrderModify(OrderTicket(),OrderOpenPrice(),SL,OrderTakeProfit(),0,clrBlue);}

              }
              

           }

     }
  }
//***************************/
 void DeleteOrders(int tip)
{

         int cnt=OrdersTotal();
         for(int i=cnt-1; i>=0; i--)
           {
            if(OrderSelect(i,SELECT_BY_POS,MODE_TRADES)==true)
            if(OrderSymbol()==Symbol() &&OrderMagicNumber()==MagicNumber&&tip==OrderType())
                 {
                 
                     close=OrderDelete(OrderTicket(),clrGray);
           }
       }
       }
       
//============ 
 void CloseOrders(int tip)
{

         int cnt=OrdersTotal();
         for(int i=cnt-1; i>=0; i--)
           {
            if(OrderSelect(i,SELECT_BY_POS,MODE_TRADES)==true)
            if(OrderSymbol()==Symbol() &&OrderMagicNumber()==MagicNumber&&tip==OrderType())
                 {
                 
                     close=OrderClose(OrderTicket(),OrderLots(),OrderClosePrice(),100000,clrRed);
           }
       }
       }
       
//============ 
 
int fnCalculatePipFactor(string pSymbol=NULL){
int value;
string broker;
if(pSymbol==NULL) pSymbol=_Symbol;
broker=AccountCompany();
value=10;
if(_Digits==2){
string symChar2=StringSubstr(pSymbol,0,2);
string symChar3=StringSubstr(pSymbol,0,3);
string symChar4=StringSubstr(pSymbol,0,4);
string symChar5=StringSubstr(pSymbol,0,5);
string symChar6=StringSubstr(pSymbol,0,6);
if(symChar2=="UK") value=int(1/_Point);
else if( symChar2=="FT") value=int(1/_Point);
else if( symChar2=="GE") value=int(1/_Point);
else if( symChar2=="DE") value=int(1/_Point);
else if( symChar2=="DA") value=int(1/_Point);
else if( symChar2==".D") value=int(1/_Point);
else if( symChar2=="#G") value=int(1/_Point);
else if( symChar2=="[D") value=int(1/_Point);
else if( symChar2=="[d") value=int(1/_Point);
else if( symChar3=="NAS") value=int(1/_Point);
else if( symChar4=="WS30") value=int(1/_Point);
else if( symChar4=="US30") value=int(1/_Point);
else if( symChar5=="US100") value=int(1/_Point);
else if( symChar5=="USTEC") value=int(1/_Point);
else if( symChar6=="IDX.DE") value=int(1/_Point);
else value=1;}
else if (_Digits==4){
if(broker=="IG Group Limited" && pSymbol=="USOIL") value=100;
else if(broker=="IG Group Limited" && pSymbol=="UKOIL") value=100;
else value=1;}
return value;}

//===============
bool fnValidateMoneyManagement(bool pUseMoneyManagement, double pRiskPercent, double pFixedLotSize){
bool result=true;
if(pUseMoneyManagement==true){
if(pRiskPercent>10){
MessageBox("The percent risk value of "+string(pRiskPercent)+"% exceeds the maximum 10% allowed by the system",
"Invalid percent risk!",MB_OK|MB_ICONEXCLAMATION);
Print("Invalid percent risk");
result=false;}}
else{double minLot=MarketInfo(_Symbol,MODE_MINLOT);
double maxLot=MarketInfo(_Symbol,MODE_MAXLOT);
if(pFixedLotSize<minLot){
MessageBox("The entered lot size is less than the minimum allowed for this market, which is "+string(minLot),
"Invalid lot size!",MB_OK|MB_ICONEXCLAMATION);
Print("Invalid lot size");
result=false;}
if(pFixedLotSize>maxLot){
MessageBox("The entered lot size is larger than the maximum allowed for this market, which is "+string(maxLot),
"Invalid lot size!",MB_OK|MB_ICONEXCLAMATION);
Print("Invalid lot size");
result=false;}}
return result;}

//===============

double MoneyManagement(string pSymbol, double pFixedVol, double pPercent, int pStopPoints){
double tradeSize;
if(pPercent>0 && pStopPoints>0){
if(pPercent>MAX_PERCENT) pPercent=MAX_PERCENT;
double margin=AccountInfoDouble(ACCOUNT_BALANCE)*(pPercent/100);
double tickSize=SymbolInfoDouble(pSymbol,SYMBOL_TRADE_TICK_VALUE);
if(tickSize==0) tickSize=fnDefaultTickSize(pSymbol);
tradeSize=(margin/pStopPoints)/tickSize;
tradeSize=VerifyVolume(pSymbol,tradeSize);
return(tradeSize);}
else{
tradeSize=pFixedVol;
tradeSize=VerifyVolume(pSymbol,tradeSize);
return(tradeSize);}}


//==============

double fnDefaultTickSize(string pSymbol=NULL){
double value;
int pipFactor;
string broker;
if(pSymbol==NULL) pSymbol=_Symbol;
pipFactor=fnCalculatePipFactor(pSymbol);
broker=AccountCompany();
value=1/pipFactor;
if(broker=="IG Group Limited"){
double convUSD=iClose("GBPUSD(£)",1,1);
if(pSymbol=="USOIL") value=0.1/convUSD;
if(pSymbol=="UKOIL") value=0.1/convUSD;}
return value;}

//=========

double VerifyVolume(string pSymbol,double pVolume){
double minVolume=SymbolInfoDouble(pSymbol,SYMBOL_VOLUME_MIN);
double maxVolume=SymbolInfoDouble(pSymbol,SYMBOL_VOLUME_MAX);
double stepVolume=SymbolInfoDouble(pSymbol,SYMBOL_VOLUME_STEP);
double tradeSize;
if(pVolume<minVolume) tradeSize=minVolume;
else if(pVolume>maxVolume) tradeSize=maxVolume;
else tradeSize=MathRound(pVolume/stepVolume)*stepVolume;
if(stepVolume>=0.1) tradeSize=NormalizeDouble(tradeSize,1);
else tradeSize=NormalizeDouble(tradeSize,2);
return(tradeSize);}




