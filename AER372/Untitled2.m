syms s t
T(s) = 1980 / (s.^2+12.*s+2000);

sols = roots([1 12 2000]);

real_s1 = real(sols(1));
imag_s1 = imag(sols(1));

real_s2 = real(sols(2));
imag_s2 = imag(sols(2));

figure(1);
plot(real_s1,imag_s1,'r*',real_s2,imag_s2,'r*');
xlabel("Real")
ylabel("Imaginary")

R(s) = 1./s;
Y(s) = T(s).*R(s);

y(t) = ilaplace(Y,s,t);

x = linspace(0,1,100);

figure(2)
plot(x, y(x));
xlabel("Time t")