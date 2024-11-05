import axios from "axios";
import React, { useState } from "react";
import toast from "react-hot-toast";
import "./Application.css";
import exampleImage from './../Hind-CV-1_page_1_img_1.png';

const Application = () => {
  const [resume, setResume] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleFileChange = (event) => {
    const file = event.target.files[0];
    setResume(file);
  };
  const renderList = (items, renderItem) => (
    items.length > 0 ? (
      <ul>
        {items.map(renderItem)}
      </ul>
    ) : (
      <p>No data available.</p>
    )
  );
  const renderSection = (title, content) => (
    <div className="result-section">
      <h5>{title}</h5>
      {content || <p>No data available.</p>}
    </div>
  );
  const handleApplication = async (e) => {
    e.preventDefault();

    if (!resume) {
      toast.error("Please select a resume file before submitting.");
      return;
    }

    const formData = new FormData();
    formData.append("pdf_file", resume);

    setLoading(true);

    try {
      const response = await axios.post(
        "http://localhost:80/extract_cv_info",
        formData,
        {
          withCredentials: true,
          headers: {
            "Content-Type": "multipart/form-data",
          },
        }
      );

      console.log("Full Response Object:", response);
      const data = response.data;
      console.log("Response Data:", data);

      setResult(data);
      toast.success(data.message || "Application submitted successfully.");
      setResume(null);
    } catch (error) {
      console.error("Error Response:", error.response);
      const errorMessage = error.response?.data?.detail || "An error occurred while submitting the application.";
      toast.error(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const getArrayData = (data) => {
    return Array.isArray(data) ? data : [];
  };

  const renderVolunteerWork = () => (
    renderList(
      result?.data?.["volunteer work"] || [],
      (volunteer, index) => (
        <li key={index}>
          <h6>{volunteer["organization name"]}</h6>
          <p><strong>Position:</strong> {volunteer.position || "Not specified"}</p>
          <p><strong>Responsibilities:</strong> {volunteer.responsibilities}</p>
        </li>
      )
    )
  );

  const renderInternships = () => (
    renderList(
      result?.data?.internship || [],
      (internship, index) => (
        <li key={index}>
          <h6>{internship["organization name"]}</h6>
          <p><strong>Duration:</strong> {internship.duration || "Not specified"}</p>
          <p><strong>Responsibilities:</strong> {internship.responsibilities}</p>
          <p><strong>Technologies:</strong> {internship.technologies || "Not specified"}</p>
        </li>
      )
    )
  );
  return (
    <section className="application">
      <div className="container">
        <h3>Resume Information Extraction</h3>
        <form onSubmit={handleApplication} className="application-form">
          <div className="form-group">
            <label>Select Resume</label>
            <input
              type="file"
              accept=".pdf"
              onChange={handleFileChange}
              className="file-input"
            />
          </div>
          <button 
            type="submit" 
            className="submit-button" 
            disabled={loading}
          >
            {loading ? "Sending..." : "Send"}
          </button>
        </form>

        {result && (
          <div className="result">
            <h4>Result:</h4>
            <div className="result-section">
              <h5>Personal Information</h5>
              <p><strong>Name:</strong> {result.data["first and last name"] || "No data available"}</p>
              <p><strong>Email:</strong> {result.data.contact?.email || "No data available"}</p>
              <p><strong>Phone:</strong> {result.data.contact?.phone || "No data available"}</p>
              <p><strong>Location:</strong> {result.data.contact?.location || "No data available"}</p>
              <p><strong>LinkedIn:</strong> {result.data.contact?.LinkedIn ? <a href={result.data.contact.LinkedIn} target="_blank" rel="noopener noreferrer">LinkedIn Profile</a> : "No data available"}</p>
              <p><strong>GitHub:</strong> {result.data.contact?.GitHub ? <a href={result.data.contact.GitHub} target="_blank" rel="noopener noreferrer">GitHub Profile</a> : "No data available"}</p>
            </div>

            <div className="result-section">
              <h5>Summary</h5>
              <p>{result.data.summary || "No data available"}</p>
            </div>
            {renderSection("Volunteer Work", renderVolunteerWork())}
            {renderSection("Internships", renderInternships())}
            <div className="result-section">
              <h5>Languages</h5>
              {result.data.languages && Object.keys(result.data.languages).length > 0 ? (
                <ul>
                  {Object.entries(result.data.languages).map(([language, proficiency]) => (
                    <li key={language}><strong>{language}:</strong> {proficiency}</li>
                  ))}
                </ul>
              ) : (
                <p>No data available.</p>
              )}
            </div>

            <div className="result-section">
              <h5>Skills</h5>
              {result.data.skills && Object.keys(result.data.skills).length > 0 ? (
                <ul>
                  {Object.entries(result.data.skills).map(([skill, level]) => (
                    <li key={skill}><strong>{skill}:</strong> {level}</li>
                  ))}
                </ul>
              ) : (
                <p>No data available.</p>
              )}
            </div>

            <div className="result-section">
              <h5>Education</h5>
              {result.data.education && Array.isArray(result.data.education) && result.data.education.length > 0 ? (
                result.data.education.map((edu, index) => (
                  <div key={index} className="education-item">
                    <h6>{edu.institution || "No data available"}</h6>
                    <p><strong>Degree:</strong> {edu.degree || "No data available"}</p>
                    <p><strong>Duration:</strong> {edu.duration || "No data available"}</p>
                  </div>
                ))
              ) : (
                <p>No data available.</p>
              )}
            </div>

            <div className="result-section">
              <h5>Interests and Hobbies</h5>
              {Array.isArray(result.data["interests and hobbies"]) && result.data["interests and hobbies"].length > 0 ? (
                <ul>
                  {result.data["interests and hobbies"].map((interest, index) => (
                    <li key={index}>{interest}</li>
                  ))}
                </ul>
              ) : (
                <p>No data available.</p>
              )}
            </div>

            <div className="result-section">
              <h5>Image Link</h5>
              {result.data["image link"] && result.data["image link"].length > 0 ? (
                <img src={"../../../" + result.data["image link"][0]} alt="Extracted" className="result-image" />
              ) : (
                <p>No data available.</p>
              )}
            </div>

            <div className="result-section">
              <h5>Links</h5>
              {getArrayData(result.data.links).length > 0 ? (
                <ul>
                  {getArrayData(result.data.links).map((link, index) => (
                    <li key={index}>
                      <a href={link.URI} target="_blank" rel="noopener noreferrer">
                        {link.Type}: {link.URI}
                      </a>
                    </li>
                  ))}
                </ul>
              ) : (
                <p>No data available.</p>
              )}
            </div>

            <div className="result-section">
              <h5>Certifications</h5>
              {getArrayData(result.data.certifications).length > 0 ? (
                <ul>
                  {getArrayData(result.data.certifications).map((certification, index) => (
                    <li key={index}>{certification}</li>
                  ))}
                </ul>
              ) : (
                <p>No data available.</p>
              )}
            </div>

            <div className="result-section">
              <h5>Projects</h5>
              {getArrayData(result.data.projects).length > 0 ? (
                getArrayData(result.data.projects).map((project, index) => (
                  <div key={index} className="project-item">
                    <h6>{project.title || "No data available"}</h6>
                    <p><strong>Description:</strong> {project.description || "No data available"}</p>
                    <p><strong>Technologies:</strong> {Array.isArray(project.technologies) && project.technologies.length > 0 ? project.technologies.join(", ") : "No data available"}</p>
                    <p><strong>Duration:</strong> {project.duration || "No data available"}</p>
                    <p><strong>Period:</strong> {Array.isArray(project.period) && project.period.length > 0 ? project.period.join(" - ") : project.period || "No data available"}</p>
                  </div>
                ))
              ) : (
                <p>No data available.</p>
              )}
            </div>

            <div className="result-section">
              <h5>Work Experience</h5>
              {getArrayData(result.data["work experience"]).length > 0 ? (
                getArrayData(result.data["work experience"]).map((work, index) => (
                  <div key={index} className="work-item">
                    <h6>{work.organization || "No data available"}</h6>
                    <p><strong>Duration:</strong> {work.date || "No data available"}</p>
                    <p><strong>Technologies:</strong> {Array.isArray(work.technologies) && work.technologies.length > 0 ? work.technologies.join(", ") : "No data available"}</p>
                    <p><strong>Responsibilities:</strong> {work.responsibilities || "No data available"}</p>
                  </div>
                ))
              ) : (
                <p>No data available.</p>
              )}
            </div>
          </div>
        )}
      </div>
    </section>
  );
};

export default Application;
