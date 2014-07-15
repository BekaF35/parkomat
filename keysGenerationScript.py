import rsa


(pub_key,priv_key)=rsa.newkeys(512);
print "private key  :	",priv_key;
print "public key   :	",pub_key;

print pub_key.save_pkcs1();
print priv_key.save_pkcs1();

privateKey=open("config/privateKey.pem",'w');
privateKey.write(priv_key.save_pkcs1());
privateKey.close();

publicKey=open("config/publicKey.pem",'w');
publicKey.write(pub_key.save_pkcs1());
publicKey.close();