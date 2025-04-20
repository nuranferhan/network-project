**Portu Başlatma / Temizleme**

1. **Port 5555'in açık olup olmadığını kontrol et:**
   ```bash
   netstat -ano | findstr :5555
   ```

2. **Eğer port kullanımda ise ilgili işlemi sonlandır:**
   - `(NO)` yerine bir önceki komuttan çıkan PID numarasını yaz:
   ```bash
   taskkill /PID (NO) /F
   ```

**Sunucuyu Başlatma**

Sunucuyu çalıştırmak için:
```bash
python main.py server
```

**İstemcileri Bağlama**

Başka bir terminal veya cihazdan istemci başlatmak için:
```bash
python main.py client
```

