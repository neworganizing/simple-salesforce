"""Simple-Salesforce Tests"""
# pylint: disable=line-too-long

SESSION_ID = '12345'
METADATA_URL = 'https://na15.salesforce.com/services/Soap/m/29.0/00Di0000000icUB'
SERVER_URL = 'https://na15.salesforce.com/services/Soap/c/29.0/00Di0000000icUB/0DFi00000008UYO'

LOGIN_RESPONSE_SUCCESS = """<?xml version="1.0" encoding="UTF-8"?>
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns="urn:enterprise.soap.sforce.com" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
   <soapenv:Body>
      <loginResponse>
         <result>
            <metadataServerUrl>%s</metadataServerUrl>
            <passwordExpired>false</passwordExpired>
            <sandbox>false</sandbox>
            <serverUrl>%s</serverUrl>
            <sessionId>%s</sessionId>
            <userId>005i0000002MUqLAAW</userId>
            <userInfo>
               <accessibilityMode>false</accessibilityMode>
               <currencySymbol>$</currencySymbol>
               <orgAttachmentFileSizeLimit>5242880</orgAttachmentFileSizeLimit>
               <orgDefaultCurrencyIsoCode>USD</orgDefaultCurrencyIsoCode>
               <orgDisallowHtmlAttachments>false</orgDisallowHtmlAttachments>
               <orgHasPersonAccounts>false</orgHasPersonAccounts>
               <organizationId>00Di0000000icUBEAY</organizationId>
               <organizationMultiCurrency>false</organizationMultiCurrency>
               <organizationName>salesforce.com</organizationName>
               <profileId>00ei0000001CMKcAAO</profileId>
               <roleId xsi:nil="true" />
               <sessionSecondsValid>7200</sessionSecondsValid>
               <userDefaultCurrencyIsoCode xsi:nil="true" />
               <userEmail>you@yourdomain.com</userEmail>
               <userFullName>Wade Wegner</userFullName>
               <userId>1234</userId>
               <userLanguage>en_US</userLanguage>
               <userLocale>en_US</userLocale>
               <userName>you@yourdomain.com</userName>
               <userTimeZone>America/Los_Angeles</userTimeZone>
               <userType>Standard</userType>
               <userUiSkin>Theme3</userUiSkin>
            </userInfo>
         </result>
      </loginResponse>
   </soapenv:Body>
</soapenv:Envelope>
""" % (METADATA_URL, SERVER_URL, SESSION_ID)


REFRESH_TOKEN_RESPONSE_SUCCESS = """'{"access_token":"%s","signature":"xxxxxxxxxuOelk8emXZqI4KDeIF2HvKHGaQ=","scope":"refresh_token full","instance_url":"%s","id":"https://login.salesforce.com/id/00D36000000kxxxxxx/005360000024xxxxxx","token_type":"Bearer","issued_at":"1471024753853"}'
""" % (SESSION_ID, SERVER_URL)
