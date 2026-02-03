from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
import os

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads/excel'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ======================
# HOME / LOGIN (DUMMY)
# ======================
@app.route('/')
def login():
    return render_template('login.html')


# ======================
# DASHBOARD
# ======================
@app.route('/dashboard')
def dashboard():
    files = os.listdir(UPLOAD_FOLDER)
    return render_template('dashboard.html', files=files)


# ======================
# UPLOAD EXCEL
# ======================
@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        file = request.files['file']
        if file:
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))
            return redirect(url_for('dashboard'))
    return render_template('upload.html')


# ======================
# BACA EXCEL & SKU
# ======================
@app.route('/batch/<filename>')
def batch(filename):
    filepath = os.path.join(UPLOAD_FOLDER, filename)

    # baca SEMUA SHEET
    xls = pd.ExcelFile(filepath)
    all_data = []

    for sheet in xls.sheet_names:
        df = pd.read_excel(xls, sheet_name=sheet)
        df['Sheet'] = sheet
        all_data.append(df)

    data = pd.concat(all_data, ignore_index=True)

    return render_template(
        'batches.html',
        tables=data.head(100).to_html(classes='table table-striped'),
        filename=filename
    )


@app.route('/search', methods=['POST'])
def search():
    sku = request.form.get('sku').strip()
    filename = request.form.get('filename')

    filepath = os.path.join(UPLOAD_FOLDER, filename)

    xls = pd.ExcelFile(filepath)
    results = []

    for sheet in xls.sheet_names:
        df = pd.read_excel(xls, sheet_name=sheet)

        # normalisasi kolom
        df.columns = df.columns.astype(str).str.lower()

        # cari kolom sku
        sku_col = None
        for col in df.columns:
            if 'sku' in col or 'article' in col or 'item' in col:
                sku_col = col
                break

        if sku_col:
            df[sku_col] = df[sku_col].astype(str).str.strip()
            found = df[df[sku_col] == sku]

            if not found.empty:
                found['Sheet'] = sheet
                results.append(found)

    if results:
        result_df = pd.concat(results)
        table = result_df.to_html(
            classes='table table-bordered table-striped',
            index=False
        )
    else:
        table = "<div class='alert alert-danger'>SKU tidak ditemukan</div>"

    return render_template(
        'batches.html',
        tables=table,
        filename=f"Hasil pencarian SKU: {sku}"
    )
    
import os

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)   
