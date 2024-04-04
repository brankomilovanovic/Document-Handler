<h1 align="center">Document handler</h1>

### About
This is a desktop application for handling a special XML (.singi) document, it was written in Python using PyQt framework.
<br><br>
Everything is stored in one XML document. Directories, documents, pages, slots and slot descriptions.
<br>
Each document has its own pages, which we can add and delete, and in each page there are 'slots' in which we can enter text or an image.
The properties of the XML document are displayed through the **QTreeWidget**, its directories and documents. And the document pages and their slots are displayed in the **QListWidget**, as well as the actual position of the slot and its content, similar to PowerPoint.
<br><hr>
### Tools used
- Python
- PyQt (PySide2/PyQt5)
- XML

<hr>

### Preview
<kbd><img src="https://user-images.githubusercontent.com/87083680/193348142-20f42de0-b48b-4d03-a35a-4a895d1657b9.png" /></kbd><hr>
<kbd><img src="https://user-images.githubusercontent.com/87083680/193348143-39fe0d1c-574c-4f9d-ab6b-a33fc570f3b8.png" /></kbd><hr>
<kbd><img src="https://user-images.githubusercontent.com/87083680/193348145-73424d4d-b29d-4f0f-abe7-9b5638fb71b3.png" /></kbd><hr>
<kbd><img src="https://user-images.githubusercontent.com/87083680/193348153-a77e5c4f-a273-4ce6-96a0-1de65928568b.png" /></kbd><hr>
<kbd><portfolio><img src="https://user-images.githubusercontent.com/87083680/193348156-b09d7483-35f3-46fb-9897-a142071b18da.png" /></portfolio></kbd><hr>
<kbd><img src="https://user-images.githubusercontent.com/87083680/193348157-7f735ac5-4da9-4625-a072-42e03e239bfc.png" /></kbd><hr>
<kbd><img src="https://user-images.githubusercontent.com/87083680/193348159-f34a141e-38e8-4a0f-84d5-20830f63b0b4.png" /></kbd><hr>
<kbd><img src="https://user-images.githubusercontent.com/87083680/193348130-d4fade54-402b-4d0b-8fab-825a3f46dc16.png" /></kbd><hr>
<kbd><img src="https://user-images.githubusercontent.com/87083680/193348136-e9ad969f-9f97-472e-b92b-853c796ddaeb.png" /></kbd><hr>

This is how the XML document looks like after editing. (it isn't the same document as in the pictures)
![12](https://user-images.githubusercontent.com/87083680/193348139-33e840cd-93e5-4bab-b815-be97c0547a7e.png)

<hr>

### How to build
**1. Open CMD**
<br>
> Windows (WinKey + R) > enter 'cmd' > navigate to the folder where you want to place the project

or<br>
> Hold Shift + Right-click > Open CMD (not PowerShell) window here
<br>

**2. Clone**
<br>
> git clone https://github.com/brankomilovanovic/Document_Handler
<br>

**3. Start ENV**
<br>
> cd Document_Handler/virtual-env/Scripts<br>
activate
<br>

**4. Start document handler**
<br>
> cd ../..<br>
py main.py

<hr>

Regards, **Branko**
