# nest-thermostat-lambda
Lambda to manage nest thermostat

* Motivation for this lambda:
  * Nest does not allow to schedule ON and OFF of thermostat, so I have to build my own automation, and I am doing by invoking their API through AWS Lambda.
  * Pre-requisite to use Nest API is documented well at Nest documentation: https://developers.google.com/nest/device-access/get-started
  * Lambda is getting triggered through AWS Eventbrite rule(cron) and turning the thermostat ON/OFF at the pre-set time depending on the event action.
  * Also, I am using the lambda to set the temperature which can be done through app too.


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

* Deployment
  * Lambda code is getting deployed through AWS Code build.