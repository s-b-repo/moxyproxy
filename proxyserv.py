const http = require('http');
const httpProxy = require('http-proxy');

// Create a proxy server instance
const proxy = httpProxy.createProxyServer({});

// Define the target proxy server(s)
const proxyServers = [
  'http://proxy1.example.com:8080',
  'http://proxy2.example.com:8080',
  'http://proxy3.example.com:8080'
];

// Simple load balancer to distribute requests
let currentProxy = 0;
const getNextProxy = () => {
  const proxy = proxyServers[currentProxy];
  currentProxy = (currentProxy + 1) % proxyServers.length;
  return proxy;
};

// Create the HTTP server
const server = http.createServer((req, res) => {
  const target = getNextProxy();
  console.log(`Forwarding request to: ${target}`);

  // Forward the request to the target proxy server
  proxy.web(req, res, { target }, (err) => {
    console.error(`Error forwarding request to ${target}:`, err);
    res.writeHead(500, { 'Content-Type': 'text/plain' });
    res.end('An error occurred.');
  });
});

// Listen on a specific port
const PORT = process.env.PORT || 3000;
server.listen(PORT, () => {
  console.log(`Proxy server is running on port ${PORT}`);
});
