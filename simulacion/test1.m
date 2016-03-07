clear
load('/home/sergio/iibm/wave_clus_2.0wb/Simulator/test/times_C_Easy1_noise01.mat')

spikes1 = zeros(1,64);
j = 0;
for i=1:3496
    if cluster_class(i) == 1
        spikes1 = spikes(i,:) + spikes1;
        j = j + 1;
    end
end

spikes2 = zeros(1,64);
j = 0;
for i=1:3496
    if cluster_class(i) == 2
        spikes2 = spikes(i,:) + spikes2;
        j = j + 1;
    end
end

spikes3 = zeros(1,64);
j = 0;
for i=1:3496
    if cluster_class(i) == 3
        spikes3 = spikes(i,:) + spikes3;
        j = j + 1;
    end
end

spikes4 = zeros(1,64);
j = 0;
for i=1:3496
    if cluster_class(i) == 4
        spikes4 = spikes(i,:) + spikes4;
        j = j + 1;
    end
end


nspikes = 90000;
tspk = 200;
length = nspikes*tspk;

signal = zeros(1,length);

for i=1:floor(nspikes/3)
    signal(tspk*i:tspk*i+63) = spikes1;
end
for i=floor(nspikes/3+1):(nspikes/3)*2
    signal(tspk*i:tspk*i+63) = spikes2;
end
for i=floor((nspikes/3)*2+1):nspikes
    signal(tspk*i:tspk*i+63) = spikes3;
end

data = signal;


%data = awgn(data, -4.7,'measured'); % 1/3
%data = awgn(data, -3.9, 'measured'); % 1/2.5
%data = awgn(data, -3,'measured'); % 1/2
%data = awgn(data, -1.7,'measured'); % 1/1.5
%data = awgn(data, -0.7,'measured'); % 1/1.2

save('spikes70000.mat','data')