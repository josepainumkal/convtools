<h2>The <span style="font-size:1.2em;">Virtual Watershed</span></h2>

<p style="text-align:right;">is a "catchment" for
software tools developed through close collaboration between watershed scientists
and software developers.</p>

<br>

<div id="abstract-blurb">
    <p>
        Our tools solve problems that our watershed scientists face today.
    </p>
    <p>
        We are working to collect these tools to form the foundation for the
        next generation of hydrological data management and modeling.
    </p>
    <p>
        Read more <a href="#who-we-are">about us</a> below
    </p>
</div>

<h2>Watersheds and Projects </h2>

<div class="row">
    <div class="col-xs-12 col-md-4">
        <h4 class="watershed-header">Valles Caldera and Jemez River Canyon</h4>
        <h5 class="state-header">New Mexico: UNM and NM Tech</h5>
    </div>

    <div class="col-xs-12 col-md-4">
        <h4 class="watershed-header">Lehman Creek</h4>
        <h5 class="state-header">Nevada: UNR and UNLV</h5>
    </div>
    <div class="col-xs-12 col-md-4">
        <h4 class="watershed-header">Dry Creek and Reynolds Creek</h4>
        <h5 class="state-header">Idaho: ISU, BSU, and UI</h5>
    </div>
</div>

<a name="who-we-are"></a>

<h2>Who we Are</h2>

<div id="who-we-are">
        <span class="who-number">13 Watershed scientists</span> working with
        <!-- <br> -->
        <span class="who-number">10 Software developers</span> across
        <!-- <br> -->
        <span class="who-number">4 watersheds</span> in
        <!-- <br> -->
        <span class="who-number">3 states:</span>
</div>

<h3>Watershed Scientists</h3>

{% for card in contributor_cards %}
    <div class="media">
  <div class="media-left">
    <a href="#">
      <img class="media-object" src={{card['photo']}} alt="...">
    </a>
  </div>
  <div class="media-body">
    <h4 class="media-heading">{{card['name']}}</h4>
    <b>Institute
  </div>
</div>
{% endfor %}