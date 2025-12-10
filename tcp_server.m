% MATLAB TCP Server Receives Commands from Python
port = 55001; % Choose a port number, must match in Python
host = "0.0.0.0"; % Listen on all available addresses

% Create TCP server object and connection status callback
t = tcpserver(host, port, "ConnectionChangedFcn", @connectionChange);

% Store object in MATLAB workspace for later access
assignin('base', 'tcpServerObj', t);
assignin('base', 'latestCmd', '');

% Set up callback for full line received
configureCallback(t, "terminator", @readTcpCallback);

fprintf('MATLAB TCP server started on port %d\n', port);
fprintf('Waiting for Python to connect...\n');

% Callback to read line
function readTcpCallback(tcpObj, ~)
    try
        data = readline(tcpObj);
        data = strtrim(data); % Remove extra spaces/newlines
        if ~isempty(data)
            assignin('base', 'latestCmd', data);
            fprintf('Received command: %s\n', data);
        end
    catch ME
        warning('Error in readTcpCallback: %s', ME.message);
    end
end

% Callback to show connection status
function connectionChange(tcpObj, ~)
    if tcpObj.Connected
        fprintf('Python connected!\n');
    else
        fprintf('Python disconnected.\n');
    end
end
