# REST_API Image Recognition service using Web Development Technologies:
Designing and Implementing Image Recognition REST API using TensorFlow, Docker, Flask, MongoDB in Python and deploying it onto AWS cloud.

- This REST API service compromises of 3 resources;
1) User Registration: User credentials will be stored in the back-end MongoDB database. Once the user registers, he/his will be given a few tokens which can be used to make API calls.
2) Image Recognition Model: The model is designed using TensorFlow and the model accepts the user input i.e. the image of an object and produces top 5 predictions of the image.
3) Token Refilling: Once the user is out of tokens, he/she can refill them using this resource. However, it requires admin permissions.

Flask was leverged to serve as a web server (locally) and Docker helped to containerize and run the REST API service on Amazon EC2. 
