package util

import (
	"fmt"
	. "gopkg.in/check.v1"
	"io/ioutil"
	"net/http"
	"net/http/httptest"
	"strings"
	"time"
	"math/rand"
)

func (s *suite) SetUpSuite(c *C) {
	s.server = httptest.NewServer(
		http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			path := "testdata/github" + r.RequestURI + "/payload"
			fmt.Printf(" -> Mocking: " + path + "\n")
			if payload, err := ioutil.ReadFile(path); err == nil {
				payloadStr := string(payload)
				payloadStr = strings.ReplaceAll(payloadStr, "https://github.com", s.server.URL)
				w.Write([]byte(payloadStr))
			} else {
				http.Error(w, "not found", http.StatusNotFound)
			}
		}))
	fmt.Printf("Smok-> SetUpSuite\n")
}

func (s *suite) TearDownSuite(c *C) {
	s.server.Close()
	fmt.Printf("Smok-> TearDownSuite\n")
}

type suite struct {
	repo *Repo
	server *httptest.Server
}

func (s *suite) SetUpTest(c *C) {
	s.repo = NewRepo(DefaultRepositoryUrl)
	s.repo.Path = c.MkDir()
	s.repo.UseS3 = false

	//defer apiServer.Close()

	s.repo.GithubURL = s.server.URL
	fmt.Printf("Smok-> SetUpTest\n")
}

var _ = Suite(&suite{})

func (s *suite) TestGithubPackageInfoRemote(c *C) {
	s.repo.ReleaseTag = "v0.53.0"
	packageName := "osv.httpserver-api"
	appPackage := s.repo.PackageInfoRemote(packageName)
	//TODO: For now let us use sleep to prevent github REST API calls fail
	// due to rate limiting. Eventually we should mock the REST api
	// (please see https://medium.com/@tech_phil/how-to-stub-external-services-in-go-8885704e8c53)
	time.Sleep(time.Duration(rand.Intn(100)) * time.Millisecond)
	c.Assert(appPackage, NotNil)
	c.Check(appPackage.Name, Equals, packageName)
}

func (s *suite) TestGithubDownloadLoaderImage(c *C) {
	s.repo.ReleaseTag = "v0.51.0"
	loaderName, err := s.repo.DownloadLoaderImage("qemu")
	time.Sleep(time.Duration(rand.Intn(100)) * time.Millisecond)
	c.Assert(err, IsNil)
	c.Check(loaderName, Equals, "osv-loader")
}

func (s *suite) TestGithubListPackagesRemote(c *C) {
	s.repo.ReleaseTag = "any"
	err := s.repo.ListPackagesRemote("")
	time.Sleep(time.Duration(rand.Intn(100)) * time.Millisecond)
	c.Assert(err, IsNil)
}

func (s *suite) TestGithubDownloadPackageRemote(c *C) {
	s.repo.ReleaseTag = "v0.53.0"
	err := s.repo.DownloadPackageRemote("osv.httpserver-api")
	time.Sleep(time.Duration(rand.Intn(100)) * time.Millisecond)
	c.Assert(err, IsNil)
}
