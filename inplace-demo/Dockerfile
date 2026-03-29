#FROM python:3.10
#WORKDIR /app
#COPY requirements.txt requirements.txt
#COPY restart-handler-scratch.py restart-handler.py
#RUN python3 -m pip install -r requirements.txt

# Use the official Go image as the base image
FROM golang:1.19

# Set the working directory inside the container
WORKDIR /app

# Copy the Go module files (if you're using Go modules)
COPY go.mod go.sum ./

# Download dependencies
RUN go mod download

# Copy the rest of the source code
COPY . .

# Build the Go application
RUN CGO_ENABLED=0 GOOS=linux go build -o main .

# Expose the port on which your app listens
EXPOSE 8080

# Command to run when the container starts
CMD ["./main"]