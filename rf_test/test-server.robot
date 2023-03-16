*** Settings ***
Documentation  Rest Testing in Robot Framework
Library  SeleniumLibrary
Library  RequestsLibrary
Library  JSONLibrary
Library  Collections

*** Test Cases ***
Asking for 'life;universe;everything' give us 42
    [documentation]  This test case verifies that the response code of the GET Request should be 200,
    ...  the response content is "42".
    Create Session  mysession  http://server:80/  verify=true
    ${response}=  GET On Session  mysession  /answer  params=search=life;universe;everything
    Status Should Be  200     ${response}  #Check Status as 200

    #Check content as "42" from Response 
     Should Be Equal As Strings  42  ${response.text}

Asking for something else give us unknown
    [documentation]  This test case verifies that the response code of the GET Request should be 404,
    ...  the response content is "unknown"
    Create Session  mysession  http://server:80/  verify=true
    ${response}=  GET On Session  mysession  /answer  expected_status=any   params=search=the truth 
    Status Should Be  404     ${response}  #Check Status as 404

    #Check content is "unknow" from Response 
     Should Be Equal As Strings  unknown  ${response.text}