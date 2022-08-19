# nest-thermostat-lambda
Lambda to manage nest thermostat

* Motivation for this lambda:
  * Nest does not allow to schedule ON and OFF of thermostat, so I have to build my own automation, and I am doing by invoking their API through AWS Lambda.
  * Pre-requisite to use Nest API is documented well at: https://developers.google.com/nest/device-access/get-started
  * Lambda is getting triggered through AWS Eventbrite rule(cron) and turning the thermostat mode ON(HEATCOOL)/OFF at the pre-set time depending on the event action.
  * Also, I am using the lambda to set the desired temperature after setting the mode ON(HEATCOOL) otherwise it will default to previous temperature.


Turning OFF event from Eventbridge:
```json
{
  "action": "OFF"
}
```

Turning ON event from Eventbridge:
```json
{
  "action": "ON"
}
```

* CD of lambda:
  * Lambda code is getting deployed through AWS Code build project.
  * AWS code build project is integrated Github repository. 
  * AWS code build and post-build actions are controlled through the buildspec.yml file.