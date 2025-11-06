import React, { useState, useRef } from 'react';
import './ImageUpload.css';

function ImageUpload({ onImageUpload, analyzing }) {
  const [dragActive, setDragActive] = useState(false);
  const [preview, setPreview] = useState(null);
  const inputRef = useRef(null);

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFile(e.dataTransfer.files[0]);
    }
  };

  const handleChange = (e) => {
    e.preventDefault();
    if (e.target.files && e.target.files[0]) {
      handleFile(e.target.files[0]);
    }
  };

  const handleFile = (file) => {
    // Validate file type
    if (!file.type.startsWith('image/')) {
      alert('Please upload an image file');
      return;
    }

    // Create preview
    const reader = new FileReader();
    reader.onloadend = () => {
      setPreview(reader.result);
    };
    reader.readAsDataURL(file);

    // Upload file
    onImageUpload(file);
  };

  const onButtonClick = () => {
    inputRef.current.click();
  };

  return (
    <div className="image-upload-container">
      <div
        className={`upload-area ${dragActive ? 'drag-active' : ''} ${analyzing ? 'analyzing' : ''}`}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
        onClick={onButtonClick}
      >
        <input
          ref={inputRef}
          type="file"
          accept="image/*"
          onChange={handleChange}
          style={{ display: 'none' }}
        />

        {preview ? (
          <div className="preview-container">
            <img src={preview} alt="Preview" className="preview-image" />
            {!analyzing && <p className="upload-text">Click or drop to change image</p>}
          </div>
        ) : (
          <div className="upload-prompt">
            <div className="upload-icon">📸</div>
            <p className="upload-text">Drag & drop an image here</p>
            <p className="upload-subtext">or click to browse</p>
            <p className="upload-formats">PNG, JPG, GIF, WebP</p>
          </div>
        )}
      </div>
    </div>
  );
}

export default ImageUpload;
